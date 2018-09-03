import queue
from common import CommonMsg, bytes_to_object


def parse_incoming_msg(sk_msg):

    def content_full(msg):
        return  f"[{msg.user['name']}] {msg.content}"

    msg = CommonMsg()
    msg.is_skype = True
    if hasattr(sk_msg, 'plain'):
        msg.content = sk_msg.plain
    msg.chat_id = sk_msg.chatId
    msg.user = {
            'id': sk_msg.user.id,
            'name': str(sk_msg.user.name)}
    msg.time = sk_msg.time

    if hasattr(sk_msg, 'file'):
        if sk_msg.file.urlThumb:
            file_obj = bytes_to_object(sk_msg.fileContent, sk_msg.file.name)
            msg.file_obj = {
                    'name': sk_msg.file.name,
                    'obj': file_obj}
            msg.content = sk_msg.file.name

    msg.content_full = content_full(msg)
    return msg
