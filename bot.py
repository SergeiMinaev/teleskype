from common import CommonMsg

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


def bot(msg):
    r = None
    if msg.content.startswith('-bot'):
        cmd = msg.content.split('-bot')[1].strip()
        if cmd == 'help': r = cmd_help(cmd)
        if r:
            r = make_msg(r, msg)
    return r
