import configparser
import random
import os
from ast import literal_eval
from common import doc, set_help

config = configparser.ConfigParser()
config.read('config.ini')

BOT_NAME = config['bot']['name']
if config['bot']['cmd_without_dash'] == 'yes':
    CMD_SIGN = ''
else:
    CMD_SIGN = '-'

aliases = literal_eval(config['bot']['show_image__aliases'])

def aliases_as_string():
    r = []
    for key in aliases.keys():
        for val in aliases[key]:
            r.append(val)
    r = ' '.join(r)
    return r


aliases_string = aliases_as_string()
s = _("""
Shows random image by specified keyword.
Available keywords:
    {aliases_string}
Example usage:
    {CMD_SIGN}{BOT_NAME} {first_aliase}""").format(
        aliases_string=aliases_string,
        first_aliase=aliases_string.split()[0],
        CMD_SIGN=CMD_SIGN,
        BOT_NAME=BOT_NAME)
@set_help(s)
@doc(f"""
    Shows random image by specified keyword. Available keywords:
        {aliases_string}
    Example usage:
        {CMD_SIGN}{BOT_NAME} bicycle
    """ )
def show_image(cmd):
    if len(cmd) == 0: return None
    for key in aliases.keys():
        for val in aliases[key]:
            if val in cmd:
                filename = random.choice(os.listdir(key))
                f = open(key + filename, 'rb')
                return f
