import queue
import gettext
import configparser
from io import BytesIO
from os import path

config = configparser.ConfigParser()
config.read('config.ini')

incoming_msg_queue = queue.Queue()

class CommonMsg():
    is_skype = False
    is_telegram = False
    chat_id = None
    user = {'id': None, 'name': None}
    time = None
    content = None
    content_full = None
    quote = None
    file_obj = {'name': None, 'obj': None}
    is_cmd = False
    cmd_conversation_name = None


def bytes_to_object(content, name):
    file_obj = BytesIO(content)
    file_obj.name = name
    return file_obj


def is_image(filename):
    extensions = ['.png', '.jpg', '.jpeg', '.gif']
    name, ext = path.splitext(filename)
    return ext.lower() in extensions


def doc(docstring):
    def document(func):
        func.__doc__ = docstring
        return func

    return document


def init_loc(user_lang = None):
    if user_lang:
        lang = user_lang
    else:
        lang = config['main']['lang']
    loc = gettext.translation('messages', localedir='./locale', languages=[lang])
    loc.install()


def set_aliases(aliases_tuple):
    """ Function decorator to add 'aliases' attribute to bot's commands """
    def wrapper(f):
        f.aliases = (aliases_tuple)
        return f
    return wrapper


def get_aliases(cmd_name):
    """
    Returns command aliases (tuple) from config.ini.
    In case of failure returns cmd_name.
    """
    try:
        return eval("%s" % config['bot_cmd_aliases'][cmd_name])
    except:
        return (cmd_name,)

def set_help(s):
    def wrapper(f):
        f.help = _(s)
        return f
    return wrapper


init_loc()
