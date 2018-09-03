import queue


incoming_msg_queue = queue.Queue()


class CommonMsg():
    is_skype = False
    is_telegram = False
    chat_id = None
    user = {'id': None, 'name': None}
    time = None
    content = None
    content_full = None
