import secrets
from common import CommonMsg
from models import Bridge

TMP_BRIDGES = []

def make_msg(text, inc_msg):
    msg = CommonMsg()
    msg.is_skype = True
    msg.is_telegram = True
    msg.chat_id = inc_msg.chat_id
    msg.user_id = inc_msg.user_id
    msg.time = inc_msg.time
    msg.content = text
    return msg


def cmd_help(cmd):
    return "Hello! I'm teleskype bot. I can't do anything yet :("


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
    print(TMP_BRIDGES)
    if msg.is_telegram:
        another_chat = 'skype'
    else:
        another_chat = 'telegram'
    result_msg = 'New bridge opened. Type this in '\
            + another_chat + ' chat:\n-bot use bridge ' + secret
    return result_msg


def use_bridge(cmd, msg):
    global TMP_BRIDGES
    secret = cmd.split('use bridge')[1].strip()
    if len(secret) == 0:
        return 'The secret code is not specified. Example: -bot use bridge 1234abcd'
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
        else:
            print(len(BRIDGE['secret']), ' is not equal to ', len(secret))

def bot(msg):
    r = None
    if msg.content.startswith('-bot'):
        cmd = msg.content.split('-bot')[1].strip()
        if cmd == 'help': r = cmd_help(cmd)
        elif cmd == 'make bridge': r = make_bridge(msg)
        elif cmd.startswith('use bridge'): r = use_bridge(cmd, msg)
        if r:
            r = make_msg(r, msg)
    return r
