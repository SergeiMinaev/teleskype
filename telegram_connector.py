import configparser
import queue
import telebot
from time import sleep
from telebot import apihelper


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
    bot.reply_to(message, message.text)
    msg_queue.put(message)


def run():
    while True:
        try:
            print("Telegram connector is running")
            bot.polling(none_stop=True, timeout=5)
        except Exception as e:
            print('telegram connector error:', repr(e))
            sleep(3)
