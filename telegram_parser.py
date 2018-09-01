import queue
from telegram_connector import msg_queue
from common import parsed_msg_queue, CommonMsg


def parse_msg():
    while True:
        tele_msg = msg_queue.get()
        if tele_msg == None: break
        msg = CommonMsg()
        msg.is_telegram = True
        msg.content = tele_msg.text
        msg.chat_id = str(tele_msg.chat.id)
        parsed_msg_queue.put(msg)
