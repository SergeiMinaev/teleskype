import telebot
import configparser
from telebot import apihelper
from common import config

token = config['main']['telegram_token']

if config['main']['use_proxy'] == "yes":
    proxy = config['proxy']
    proxy_string = f"{proxy['proxy_type']}://{proxy['login']}:{proxy['password']}"
    proxy_string += f"@{proxy['hostname']}:{proxy['port']}"
    apihelper.proxy = {'https': proxy_string}


bot = telebot.TeleBot(token)
