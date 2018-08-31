import queue
from telegram_connector import msg_queue

parsed_msg_queue = queue.Queue()

class CommonMsg:
    is_skype = False
    is_telegram = True
    chat_id = None
    user_id = None
    time = None
    content = None

def parse_msg():
    while True:
        tele_msg = msg_queue.get()
        if tele_msg == None: break
        msg = CommonMsg()
        msg.content = tele_msg.text
        parsed_msg_queue.put(msg)
