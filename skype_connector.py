import configparser
import os
import queue
import uuid
from threading import Thread, Timer
from datetime import datetime
from time import sleep
from skpy import Skype, SkypeAuthException, SkypeEventLoop
from hub import outgoing_sk_msg_queue
from common import incoming_msg_queue, is_image
from skype_parser import parse_incoming_msg

TOKEN_FILE="skype_token"

config = configparser.ConfigParser()
config.read('config.ini')

msg_to_skype_queue = queue.Queue()

class MySkype(SkypeEventLoop):
    def onEvent(self, event):
        if event.type == 'NewMessage' and type(event).__name__ == 'SkypeNewMessageEvent':
            if event.msg.user:
                # ignore self
                if event.msg.user.id != self.user.id:
                    #event.msg.chat.sendMsg(event.msg.content)
                    msg = parse_incoming_msg(event.msg)
                    incoming_msg_queue.put(msg)

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
        chat_id = None
        if not outgoing['bridge']: # direct message
            chat_id = outgoing['msg'].chat_id
        elif outgoing['msg'].is_telegram: # forwarded message from telegram to skype
            chat_id = outgoing['bridge'].skype_id
        if chat_id:
            chat = sk.chats.chat(chat_id)
            if outgoing['msg'].content_full:
                chat.sendMsg(outgoing['msg'].content_full)
            if outgoing['msg'].file_obj['obj']:
                print('going to send file')
                if is_image(outgoing['msg'].file_obj['name']):
                    outgoing['msg'].file_obj['obj'].seek(0)
                    chat.sendFile(
                            outgoing['msg'].file_obj['obj'],
                            outgoing['msg'].file_obj['name'],
                            image = True)
                else:
                    chat.sendFile(
                            outgoing['msg'].file_obj['obj'],
                            outgoing['msg'].file_obj['name'],
                            image = False)


def status_checker(sk):
    while True:
        mood = uuid.uuid4().hex.upper()[0:6]
        status = 'error'
        try:
            sk.setMood(mood)
            status = 'ok'
        except:
            pass
        f = open('skype_status.txt', 'w')
        f.write(status)
        f.close()
        sleep(15)


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
    status_thread = Thread(target = status_checker, args=(sk,)).start()
    check_token_loop(sk.conn)
