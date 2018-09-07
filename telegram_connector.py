import configparser
import queue
import telebot
from io import BytesIO
from PIL import Image
from threading import Thread
from time import sleep
from telebot import apihelper
from hub import outgoing_tele_msg_queue
from common import incoming_msg_queue, is_image, bytes_to_object
from telegram_parser import parse_incoming_msg

config = configparser.ConfigParser()
config.read('config.ini')
token = config['main']['telegram_token']

if config['main']['use_proxy'] == "yes":
    proxy = config['proxy']
    proxy_string = f"{proxy['proxy_type']}://{proxy['login']}:{proxy['password']}"
    proxy_string += f"@{proxy['hostname']}:{proxy['port']}"
    apihelper.proxy = {'https': proxy_string}


bot = telebot.TeleBot(token)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hello!")


# Handle all messages with content_type 'text'
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    #bot.reply_to(message, message.text)
    message = parse_incoming_msg(message)
    incoming_msg_queue.put(message)


@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    photo_file = bot.get_file(message.photo[len(message.photo)-1].file_id)
    photo_content = bot.download_file(photo_file.file_path)
    file_obj = bytes_to_object(photo_content, photo_file.file_path.split('/')[-1])
    message = parse_incoming_msg(message, content_type='photo', file_obj=file_obj)
    incoming_msg_queue.put(message)


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message):
    photo_file = bot.get_file(message.sticker.file_id)
    photo_content = bot.download_file(photo_file.file_path)
    filename = photo_file.file_path.split('/')[-1]
    file_obj = bytes_to_object(photo_content, filename)
    png_obj = BytesIO()
    im = Image.open(file_obj).convert('RGBA')
    im.save(png_obj, format='PNG')
    file_obj.close()
    png_obj.seek(0)
    message = parse_incoming_msg(message, content_type='photo', file_obj=png_obj)
    incoming_msg_queue.put(message)


@bot.message_handler(content_types=['video'])
def video_handler(message):
    file_id= bot.get_file(message.video.file_id)
    file_name = file_id.file_path.split('/')[-1]
    file_content = bot.download_file(file_id.file_path)
    file_obj = bytes_to_object(file_content, file_name)
    file_obj.name = file_name
    message = parse_incoming_msg(message, content_type='video', file_obj=file_obj)
    incoming_msg_queue.put(message)


def outgoing_handler():
    while True:
        outgoing = outgoing_tele_msg_queue.get()
        if outgoing == None: break
        chat_id = None
        if not outgoing['bridge']: # direct message
            chat_id = outgoing['msg'].chat_id
        elif outgoing['msg'].is_skype: # forwarded message from skype to telegram
            chat_id = outgoing['bridge'].telegram_id
        if chat_id:
            if outgoing['msg'].content_full:
                bot.send_message(
                        chat_id,
                        outgoing['msg'].content_full,
                        parse_mode='HTML')
            if outgoing['msg'].file_obj['obj']:
                outgoing['msg'].file_obj['obj'].seek(0)
                if is_image(outgoing['msg'].file_obj['name']):
                    bot.send_photo(
                            chat_id,
                            outgoing['msg'].file_obj['obj'])
                else:
                    bot.send_document(
                            chat_id,
                            outgoing['msg'].file_obj['obj'])


def status_checker():
    while True:
        try:
            me = bot.get_me()
            set_connection_status('ok')
        except:
            set_connection_status('error')
        sleep(15)


def set_connection_status(status):
    f = open("telegram_status.txt", "w")
    f.write(status)
    f.close()


def run():
    outgoing_thread = Thread(target = outgoing_handler).start()
    while True:
        try:
            sleep(3)
            print('>>>> Telegram connector is running')
            status_thread = Thread(target = status_checker).start()
            bot.polling(none_stop=True, timeout=5)
        except Exception as e:
            print('>>>> Telegram connector error:', repr(e))
            set_connection_status('error')
