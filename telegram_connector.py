import configparser
import queue
import telebot
from threading import Thread
from time import sleep
from telebot import apihelper
from hub import outgoing_tele_msg_queue
from common import incoming_msg_queue
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
            bot.send_message(
                    chat_id,
                    outgoing['msg'].content_full,
                    parse_mode='HTML')


def run():
    outgoing_thread = Thread(target = outgoing_handler).start()
    while True:
        try:
            print("Telegram connector is running")
            bot.polling(none_stop=True, timeout=5)
        except Exception as e:
            print('telegram connector error:', repr(e))
            sleep(3)
