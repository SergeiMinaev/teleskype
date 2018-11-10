import re
import secrets
import configparser
import random
from common import (
        CommonMsg,
        init_loc,
        get_aliases,
        set_aliases,
        set_help
        )
from models import Bridge
from bot.show_image import show_image
from bot.cbr_currency import cbr_currency
from bot.stats import stats, write_stats, say_random


config = configparser.ConfigParser()
config.read('config.ini')

TMP_BRIDGES = []
BOT_NAME = config['bot']['name']
if config['bot']['cmd_without_dash'] == 'yes':
    CMD_SIGN = ''
else:
    CMD_SIGN = '-'


def make_msg(response, inc_msg):
    msg = CommonMsg()
    msg.is_skype = True
    msg.is_telegram = True
    msg.chat_id = inc_msg.chat_id
    msg.user = inc_msg.user
    msg.time = inc_msg.time
    if hasattr(response, 'read'): # if response is file-like object
        msg.file_obj = {'name': 'image.jpg', 'obj': response}
    else:
        msg.content = response
        msg.content_full = f'[{BOT_NAME}] {response}'
    return msg

@set_aliases(get_aliases('help'))
def cmd_help(cmd):
    result = _("""Available commands:
    {CMD_SIGN}{BOT_NAME} make bridge - creates a new bridge and returns a secret code.
    {CMD_SIGN}{BOT_NAME} use bridge [secret code] - tries to connect to another chat with \
specified secret code.
    {CMD_SIGN}{BOT_NAME} set lang [lang] - change language.
    {CMD_SIGN}{BOT_NAME} ping - {ping_help}

Available modules:
    show_image
Type {CMD_SIGN}{BOT_NAME} help [module name] to get help on a specific module.
    """).format(CMD_SIGN=CMD_SIGN, BOT_NAME=BOT_NAME, ping_help=ping.help)
    return result

def module_help(cmd):
    module_name = cmd.split('help')[1].strip().lower()
    bot_module = None
    doc_string = None
    try:
        bot_module = globals()[module_name]
    except:
        return _("Module {0} not found").format(module_name)
    if bot_module:
        doc_string = bot_module.help.strip()
    if not doc_string:
        result = f"Module {module_name} doesn't have a documentation"
    else:
        result = f"""
{module_name} help:
{doc_string}
"""
    return result

def make_bridge(msg):
    global TMP_BRIDGES
    secret = secrets.token_hex(nbytes=4)
    if msg.is_telegram:
        telegram_id = msg.chat_id
    else:
        telegram_id = None
    if msg.is_skype:
        skype_id = msg.chat_id
    else:
        skype_id = None
    TMP_BRIDGES.append({
        'secret': secret,
        'telegram_id': telegram_id,
        'skype_id': skype_id})
    if msg.is_telegram:
        another_chat = 'skype'
    else:
        another_chat = 'telegram'
    result_msg = f"""New bridge opened. \
Type this in {another_chat} chat:\n{CMD_SIGN}{BOT_NAME} use bridge {secret}"""
    return result_msg


def use_bridge(cmd, msg):
    global TMP_BRIDGES
    secret = cmd.split('use bridge')[1].strip()
    if len(secret) == 0:
        return f"""The secret code is not specified. \n
Example: {CMD_SIGN}{BOT_NAME} use bridge 1234abcd"""
    for BRIDGE in TMP_BRIDGES:
        if BRIDGE['secret'] == secret:
            if msg.is_skype:
                BRIDGE['skype_id'] = msg.chat_id
            elif msg.is_telegram:
                BRIDGE['telegram_id'] = msg.chat_id
            Bridge.create(
                    telegram_id = BRIDGE['telegram_id'],
                    skype_id = BRIDGE['skype_id'])
            return 'The connection is established successfully'

s = _("ping? pong!")
@set_aliases(get_aliases('ping'))
@set_help(s)
def ping():
    return _('pong')


def set_lang(cmd):
    lang = cmd.split('set lang')[1].strip().lower()
    try:
        init_loc(lang)
        return _("Language is set to: {0}").format(lang)
    except:
        return _("Can't set language to: {0}").format(lang)


def bot(msg):
    r = None

    write_stats(msg)

    if len(re.split(fr'^{CMD_SIGN}{BOT_NAME}[.!?, ]', msg.content,
            re.IGNORECASE)) == 2:
        cmd = re.split(fr'^{CMD_SIGN}{BOT_NAME}[.!?, ]', msg.content,
                re.IGNORECASE)[1].strip()
        if cmd in cmd_help.aliases: r = cmd_help(cmd)
        elif cmd.startswith('help'): r = module_help(cmd)
        elif cmd == 'make bridge': r = make_bridge(msg)
        elif cmd in ping.aliases: r = ping()
        elif cmd.startswith('use bridge'): r = use_bridge(cmd, msg)
        elif cmd.startswith('set lang'): r = set_lang(cmd)
        elif cmd.startswith(cbr_currency.aliases): r = cbr_currency(cmd)
        elif cmd.startswith(stats.aliases): r = stats(cmd)
        else:
            r = show_image(cmd)
        if not r:
            r = say_random()

        if r:
            r = make_msg(r, msg)
    return r
