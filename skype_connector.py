import configparser
import os
from threading import Thread, Timer
import queue
from datetime import datetime
from time import sleep
from skpy import Skype, SkypeAuthException, SkypeEventLoop
from hub import outgoing_sk_msg_queue

TOKEN_FILE="skype_token"

config = configparser.ConfigParser()
config.read('config.ini')

msg_queue = queue.Queue()
msg_to_skype_queue = queue.Queue()

class MySkype(SkypeEventLoop):
    def onEvent(self, event):
        if event.type == 'NewMessage' and type(event).__name__ == 'SkypeNewMessageEvent':
            if event.msg.user:
                # ignore self
                if event.msg.user.id != self.user.id:
                    #event.msg.chat.sendMsg(event.msg.content)
                    msg_queue.put(event.msg)

def check_token_loop(conn):
    Timer(300, check_token_loop, [conn]).start()
    token_t = conn.tokenExpiry['skype'].timestamp()
    now_t = datetime.now().timestamp()
    if token_t - now_t < 600:
        print("Trying to refresh skype token...")
        try:
            conn.refreshSkypeToken()
        except SkypeAuthException as e:
            print("Can't refresh skype token. Login request is rejected",
                    repr(e))
        except SkypeApiException as e:
            print("Can't refresh skype token. Login form can't be processed",
                    repr(e))
        else:
            print("Skype token has been refreshed successfully")

def outgoing_handler(sk):
    while True:
        outgoing = outgoing_sk_msg_queue.get()
        if outgoing == None: break
        if outgoing['msg'].is_telegram:
            chat = sk.chats.chat(outgoing['bridge'].skype_id)
            chat.sendMsg(outgoing['msg'].content)

def loop(sk):
    sk.loop()

def run():
    print("Skype connector is running")
    sk = Skype(connect=False)
    sk.conn.setTokenFile(TOKEN_FILE)
    try:
        sk.conn.readToken()
    #token file has expired or doesn't exist or not readable
    except SkypeAuthException:
        sk.conn.setUserPwd(config['main']['skype_login'],
                config['main']['skype_password'])
        sk.conn.getSkypeToken()

    sk = MySkype(tokenFile = TOKEN_FILE, autoAck = True)

    loop_thread = Thread(target = loop, args=(sk,)).start()
    outgoing_thread = Thread(target = outgoing_handler, args=(sk,)).start()
    check_token_loop(sk.conn)
