import queue
from common import CommonMsg


def parse_incoming_msg(sk_msg):

    def content_full(msg):
        return  f"[{msg.user['name']}] {msg.content}"

    msg = CommonMsg()
    msg.is_skype = True
    msg.content = sk_msg.plain
    msg.chat_id = sk_msg.chatId
    msg.user = {
            'id': sk_msg.user.id,
            'name': str(sk_msg.user.name)}
    msg.time = sk_msg.time
    msg.content_full = content_full(msg)
    return msg
