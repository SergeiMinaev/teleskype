import configparser
import os
import threading
import queue
from datetime import datetime
from time import sleep
from skpy import Skype, SkypeAuthException, SkypeEventLoop

TOKEN_FILE="skype_token"

config = configparser.ConfigParser()
config.read('config.ini')

msg_queue = queue.Queue()


class MySkype(SkypeEventLoop):
    def onEvent(self, event):
        if event.type == 'NewMessage' and type(event).__name__ == 'SkypeNewMessageEvent':
            if event.msg.user:
                # ignore self
                if event.msg.user.id != self.user.id:
                    event.msg.chat.sendMsg(event.msg.content)
                    msg_queue.put(event.msg)

def check_token_loop(conn):
    threading.Timer(300, check_token_loop, [conn]).start()
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

    sk_loop = MySkype(tokenFile = TOKEN_FILE, autoAck = True)
    sk_loop.loop()

    check_token_loop(sk.conn)
