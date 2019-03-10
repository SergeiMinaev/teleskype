import configparser
import queue
import telebot
import logging
from io import BytesIO
from PIL import Image
from threading import Thread
from time import sleep
from telebot import apihelper
from hub import outgoing_tele_msg_queue
from telegram_common import bot
from common import (
        config,
        incoming_msg_queue,
        is_image,
        )
from telegram_parser import parse_incoming_msg


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hello!")


@bot.message_handler(content_types=['text', 'photo', 'sticker', 'video', 'document'])
def photo_handler(message):
    message = parse_incoming_msg(message)
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
        if chat_id and not outgoing['msg'].is_cmd:
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
        if outgoing['msg'].is_cmd:
            if outgoing['msg'].cmd_conversation_name:
                bot.set_chat_title(
                        chat_id,
                        outgoing['msg'].cmd_conversation_name)


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
            print('Telegram connector is running')
            status_thread = Thread(target = status_checker).start()
            bot.polling(none_stop=True, timeout=5)
        except Exception as e:
            logging.error('Telegram connector error:', repr(e))
            set_connection_status('error')
            sleep(3)
