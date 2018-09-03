from common import CommonMsg



def parse_incoming_msg(tele_msg):

    def content_full(msg):
        return  f"[{msg.user['name']}] {msg.content}"

    msg = CommonMsg()
    msg.is_telegram = True
    msg.user = {
            'id': tele_msg.from_user.id,
            'name': tele_msg.from_user.username}
    msg.content = tele_msg.text
    msg.chat_id = str(tele_msg.chat.id)
    msg.content_full = content_full(msg)
    return msg
