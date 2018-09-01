import queue

parsed_msg_queue = queue.Queue()

class CommonMsg():
    is_skype = False
    is_telegram = False
    chat_id = None
    user_id = None
    time = None
    content = None
