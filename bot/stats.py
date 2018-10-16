from peewee import *
from bot.models import db, User, Message
from common import (
        config,
        doc,
        set_help,
        set_aliases,
        get_aliases
        )
from datetime import datetime


BOT_NAME = config['bot']['name']
if config['bot']['cmd_without_dash'] == 'yes':
    CMD_SIGN = ''
else:
    CMD_SIGN = '-'


s = _("""Stores users and messages. Show statistics.
Example usage:
    {CMD_SIGN}{BOT_NAME} {first_aliase}""").format(
            first_aliase=get_aliases('stats')[0],
            CMD_SIGN=CMD_SIGN,
            BOT_NAME=BOT_NAME)
@set_aliases(get_aliases('stats'))
@set_help(s)
def stats(cmd):
    msg_q = Message.select()
    msgs = [msg for msg in msg_q]
    s = _("""Total number of messages:
    {msg_count}""").format(
            msg_count=len(msgs))
    return s

def write_stats(msg):
    if msg.content:
        db.connect(reuse_if_open=True)
        db.create_tables([User, Message])
        user_q = User.select().where(User.user_id == msg.user['id'])
        users = [user for user in user_q]
        if len(users) == 0:
            is_telegram = True if msg.is_telegram else False
            user = User.create(
                    user_id=msg.user['id'],
                    is_telegram=is_telegram,
                    username=msg.user['name'])
            user.save()
        else:
            user = users[0]
        msg = Message.create(
                user=user,
                message=msg.content,
                timestamp=round(datetime.now().timestamp()))
        msg.save()
