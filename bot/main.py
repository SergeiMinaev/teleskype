import secrets
import configparser
from common import CommonMsg
from models import Bridge


config = configparser.ConfigParser()
config.read('config.ini')

TMP_BRIDGES = []
BOT_NAME = config['bot']['name']
if config['bot']['cmd_without_dash'] == 'yes':
    CMD_SIGN = ''
else:
    CMD_SIGN = '-'

def make_msg(text, inc_msg):
    msg = CommonMsg()
    msg.is_skype = True
    msg.is_telegram = True
    msg.chat_id = inc_msg.chat_id
    msg.user = inc_msg.user
    msg.time = inc_msg.time
    msg.content = text
    msg.content_full = f'[{BOT_NAME}] {text}'
    return msg


def cmd_help(cmd):
    result = f"""Available commands:
    {CMD_SIGN}{BOT_NAME} make bridge - creates a new bridge and returns a secret code.
    {CMD_SIGN}{BOT_NAME} use bridge [secret code] - tries to connect to another chat with \
specified secret code.
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

def bot(msg):
    r = None
    if msg.content.startswith(f'{CMD_SIGN}{BOT_NAME}'):
        cmd = msg.content.split(f'{BOT_NAME}')[1].strip()
        if cmd == 'help': r = cmd_help(cmd)
        elif cmd == 'make bridge': r = make_bridge(msg)
        elif cmd.startswith('use bridge'): r = use_bridge(cmd, msg)
        if r:
            r = make_msg(r, msg)
    return r
