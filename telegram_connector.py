import configparser
import queue
import telebot
from threading import Thread
from time import sleep
from telebot import apihelper
from hub import outgoing_tele_msg_queue

config = configparser.ConfigParser()
config.read('config.ini')
token = config['main']['telegram_token']

if config['main']['use_proxy'] == "yes":
    proxy = config['proxy']
    proxy_string = f"{proxy['proxy_type']}://{proxy['login']}:{proxy['password']}"
    proxy_string += f"@{proxy['hostname']}:{proxy['port']}"
    apihelper.proxy = {'https': proxy_string}

msg_queue = queue.Queue()

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hello!")


# Handle all messages with content_type 'text'
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    #bot.reply_to(message, message.text)
    msg_queue.put(message)


def outgoing_handler():
    while True:
        outgoing = outgoing_tele_msg_queue.get()
        if outgoing == None: break
        if outgoing['bot_direct_msg']:
            if outgoing['msg'].is_telegram:
                bot.send_message(
                        outgoing['msg'].chat_id,
                        outgoing['msg'].content,
                        parse_mode='HTML')
        elif outgoing['msg'].is_skype:
            bot.send_message(
                    outgoing['bridge'].telegram_id,
                    outgoing['msg'].content,
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
