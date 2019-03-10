import queue
from common import incoming_msg_queue
from models import db, Bridge
from bot.main import bot


query = Bridge.select()
try:
    bridges = [bridge for bridge in query]
except:
    bridges = []

outgoing_tele_msg_queue = queue.Queue()
outgoing_sk_msg_queue = queue.Queue()


def find_the_bridge(msg):
    bridge = None
    if msg.is_skype:
        for b in bridges:
            if b.skype_id == msg.chat_id:
                bridge = b
    if msg.is_telegram:
        for b in bridges:
            if b.telegram_id == msg.chat_id:
                bridge = b
    return bridge


def forward_to_bridge(bridge, bot_response, to_telegram=True, to_skype=True):
    if to_telegram:
        outgoing_tele_msg_queue.put({
            'bridge': bridge,
            'msg': bot_response})
    if to_skype:
        outgoing_sk_msg_queue.put({
            'bridge': bridge,
            'msg': bot_response})

def hub():
    while True:
        msg = incoming_msg_queue.get()
        if msg == None: break
        bridge = find_the_bridge(msg)
        if bridge:
            forward_to_bridge(bridge, msg)
        bot_response = None
        if not msg.is_cmd:
            if not msg.file_obj['obj']:
                bot_response = bot(msg)
            if bot_response:
                if bridge:
                    forward_to_bridge(bridge, bot_response)
                else:
                    to_telegram = msg.is_telegram
                    to_skype = msg.is_skype
                    forward_to_bridge(None, bot_response, to_telegram, to_skype)
