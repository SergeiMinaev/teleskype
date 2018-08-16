import configparser
from time import sleep
import telebot
from telebot import apihelper


config = configparser.ConfigParser()
config.read('config.ini')
token = config['main']['telegram_token']
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
    bot.reply_to(message, message.text)


def run():
    while True:
        try:
            print("Telegram connector is running")
            bot.polling(none_stop=True, timeout=5)
        except Exception as e:
            print('telegram connector error:', repr(e))
            sleep(3)
