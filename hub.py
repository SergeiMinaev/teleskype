import queue
from common import parsed_msg_queue
from models import db, Bridge
from bot import bot


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


def forward_to_bridge(bridge, msg, bot_direct_msg=False):
    outgoing_tele_msg_queue.put({
        'bridge': bridge,
        'msg': msg,
        'bot_direct_msg': bot_direct_msg})
    outgoing_sk_msg_queue.put({
        'bridge': bridge,
        'msg': msg,
        'bot_direct_msg': bot_direct_msg})


def handle_bot_response_direct(msg, bot_response):
    bot_response.is_skype = msg.is_skype
    bot_response.is_telegram = msg.is_telegram
    forward_to_bridge(None, bot_response, True)


def hub():
    while True:
        msg = parsed_msg_queue.get()
        if msg == None: break
        bridge = find_the_bridge(msg)
        if bridge:
            forward_to_bridge(bridge, msg)
        bot_response = bot(msg)
        if bot_response:
            if bridge:
                forward_to_bridge(bridge, bot_response)
            else:
                handle_bot_response_direct(msg, bot_response)
