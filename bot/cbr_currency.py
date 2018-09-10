import configparser
import random
import os
import requests
from common import doc, set_help, set_aliases, get_aliases
from lxml import etree

config = configparser.ConfigParser()
config.read('config.ini')

BOT_NAME = config['bot']['name']
if config['bot']['cmd_without_dash'] == 'yes':
    CMD_SIGN = ''
else:
    CMD_SIGN = '-'

URL = 'http://www.cbr.ru/scripts/XML_daily.asp'

def get_available_currencies():
    cur_list = []
    r = requests.get(URL)
    tree = etree.fromstring(r.content)
    tree = tree.getroottree()
    root = tree.getroot()
    for node in root:
        cur_list.append(node.find('CharCode').text)
    return ' '.join(cur_list)


s = _("""Returns currency rates from Central Bank of Russia (cbr.ru)
Available currencies:
    {currencies}
Example usage:
    {CMD_SIGN}{BOT_NAME} {first_aliase} USD
    {CMD_SIGN}{BOT_NAME} {first_aliase} usd""").format(
        first_aliase=get_aliases('cbr_currency')[0],
        CMD_SIGN=CMD_SIGN,
        BOT_NAME=BOT_NAME,
        currencies=get_available_currencies())
@set_aliases(get_aliases('cbr_currency'))
@set_help(s)
def cbr_currency(cmd):
    if len(cmd) == 0: return None
    if " " in cmd:
        currency = cmd.split()[1].strip()
    else:
        currency = None

    if currency:
        r = requests.get(URL)
        tree = etree.fromstring(r.content)
        tree = tree.getroottree()
        root = tree.getroot()
        msg = _("Exchange rate of ")
        for node in root:
            if node.find('CharCode').text.lower() == currency.lower():
                char_code = node.find('CharCode').text
                nominal = node.find('Nominal').text
                name = node.find('Name').text
                value = node.find('Value').text
                return _("""{msg} {char_code}:
    {nominal} {name} - {value} RUB""".format(msg=msg,
        char_code=char_code, nominal=nominal, name=name, value=value))

        err_msg = _("""Unknown currency. Available currencies:
        {currencies}""".format(currencies=get_available_currencies()))
        return err_msg
    else:
        return s
