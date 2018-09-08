from common import CommonMsg

def parsed_message(msg):
    if msg.reply_to_message:
        text = "{quoted_text}".format(
                quoted_text=msg.reply_to_message.text)
        text += "\n<<< {0}".format(msg.text)
        return text
    else:
        return msg.text

def parsed_name(msg):
    if msg.from_user.first_name and msg.from_user.last_name:
        return f'{msg.from_user.first_name} {msg.from_user.last_name}'
    elif msg.from_user.first_name:
        return f'{msg.from_user.first_name}'
    elif msg.from_user.username:
        return msg.from_user.username
    else:
        return msg.from_user.id

def parse_incoming_msg(tele_msg, content_type='text', file_obj=None):

    def content_full(msg):
        return  f"[{msg.user['name']}] {msg.content}"

    msg = CommonMsg()
    msg.is_telegram = True
    msg.user = {
            'id': tele_msg.from_user.id,
            'name': parsed_name(tele_msg)}
    msg.content = parsed_message(tele_msg)
    msg.chat_id = str(tele_msg.chat.id)

    if content_type == 'photo':
        msg.content = 'Image.jpg:'
        msg.file_obj = {
                'name': 'Image.jpg',
                'obj': file_obj}

    if content_type == 'video':
        msg.content = f'{file_obj.name}:'
        msg.file_obj = {
                'name': file_obj.name,
                'obj': file_obj}

    if content_type == 'document':
        msg.content = f'{file_obj.name}:'
        msg.file_obj = {
                'name': file_obj.name,
                'obj': file_obj}

    msg.content_full = content_full(msg)
    return msg
