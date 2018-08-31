#!/usr/bin/env python
import signal
import sys
from threading import Thread
import telegram_connector
import skype_connector
import skype_parser
import telegram_parser
import hub
from models import db, Bridge


def ctrl_c_handler(sig, frame):
    db.close()
    sys.exit(0)


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Bridge])


signal.signal(signal.SIGINT, ctrl_c_handler)


skype_thread = Thread(target = skype_connector.run).start()
telegram_thread = Thread(target = telegram_connector.run).start()
skype_parser_thread = Thread(target = skype_parser.parse_msg).start()
telegram_parser_thread = Thread(target = telegram_parser.parse_msg).start()
hub_thread = Thread(target = hub.hub).start()
