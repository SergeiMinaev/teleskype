import re
from common import CommonMsg, bytes_to_object
from telegram_common import bot


def file_obj_from_msg(msg):
    if msg.content_type == 'photo':
        photo_file = bot.get_file(msg.photo[len(msg.photo)-1].file_id)
        photo_content = bot.download_file(photo_file.file_path)
        file_obj = bytes_to_object(photo_content, photo_file.file_path.split('/')[-1])
    elif msg.content_type == 'sticker':
        photo_file = bot.get_file(msg.sticker.file_id)
        photo_content = bot.download_file(photo_file.file_path)
        filename = photo_file.file_path.split('/')[-1]
        tmp_file_obj = bytes_to_object(photo_content, filename)
        file_obj = BytesIO()
        im = Image.open(tmp_file_obj).convert('RGBA')
        im.save(file_obj, format='PNG')
        tmp_file_obj.close()
        file_obj.seek(0)
    elif msg.content_type == 'video' or msg.content_type == 'document':
        if msg.content_type == 'video':
            file_id = bot.get_file(msg.video.file_id)
        else:
            file_id = bot.get_file(msg.document.file_id)
        file_name = file_id.file_path.split('/')[-1]
        file_content = bot.download_file(file_id.file_path)
        file_obj = bytes_to_object(file_content, file_name)
        file_obj.name = file_name
    return file_obj

def make_hyperlinks(text):
    text = re.sub(r'(https?://[^\s]+)', r'<a href="\g<1>">\g<1></a>', text)
    return text

def parsed_message(msg):
    if msg.reply_to_message:
        if msg.reply_to_message.text:
            if not msg.reply_to_message.from_user.is_bot:
                quoted_name = parsed_name(msg.reply_to_message)
                text = "\n>>> [{quoted_name}] {quoted_text}".format(
                        quoted_name=quoted_name,
                        quoted_text=msg.reply_to_message.text)
            else:
                text = "\n>>> {quoted_text}".format(
                        quoted_text=msg.reply_to_message.text)

            text += "\n>>>\n {0}".format(msg.text)
            return text
    msg.text = make_hyperlinks(msg.text)
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

def parse_incoming_msg(tele_msg):

    def content_full(msg):
        return  f"[{msg.user['name']}] {msg.content}"

    msg = CommonMsg()
    msg.is_telegram = True
    msg.user = {
            'id': tele_msg.from_user.id,
            'name': parsed_name(tele_msg)}
    msg.content = parsed_message(tele_msg)
    msg.chat_id = str(tele_msg.chat.id)

    if tele_msg.content_type != 'text':
        file_obj = file_obj_from_msg(tele_msg)
        msg.content = f'{file_obj.name}:'
        msg.file_obj = {
                'name': file_obj.name,
                'obj': file_obj}

    msg.content_full = content_full(msg)

    return msg
