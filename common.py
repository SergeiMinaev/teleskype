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
    file_obj = {'name': None, 'obj': None}


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
