from telegram_parser import parsed_msg_queue

def hub():
    while True:
        msg = parsed_msg_queue.get()
        if msg == None: break
        print('HUB:', msg.is_skype, msg.is_telegram, msg.content)
