from skype_connector import msg_queue

class CommonMsg:
    is_skype = True
    is_telegram = False
    chat_id = None
    user_id = None
    time = None
    content = None

def parse_msg():
    while True:
        sk_msg = msg_queue.get()
        if sk_msg == None: break
        msg = CommonMsg()
        msg.content = sk_msg.plain
        msg.chat_id = sk_msg.chatId
        msg.user_id = sk_msg.userId
        msg.time = sk_msg.time
        print('--------')
        print('Skype: ', msg.time, msg.chat_id, msg.user_id, msg.content)
        print('--------')
