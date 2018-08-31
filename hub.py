import queue
from common import parsed_msg_queue
from models import db, Bridge


query = Bridge.select()
bridges = [bridge for bridge in query]

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


def forward_to_bridge(bridge, msg):
    outgoing_tele_msg_queue.put({'bridge': bridge, 'msg': msg})
    outgoing_sk_msg_queue.put({'bridge': bridge, 'msg': msg})


def hub():
    while True:
        msg = parsed_msg_queue.get()
        if msg == None: break
        bridge = find_the_bridge(msg)
        if bridge:
            forward_to_bridge(bridge, msg)
