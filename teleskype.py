#!/usr/bin/env python
import signal
import sys
from threading import Thread
import telegram_connector
import skype_connector
import hub
from models import db, Bridge


def ctrl_c_handler(sig, frame):
    db.close()
    sys.exit(0)


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Bridge])


signal.signal(signal.SIGINT, ctrl_c_handler)
init_db()

skype_thread = Thread(target = skype_connector.run).start()
telegram_thread = Thread(target = telegram_connector.run).start()
hub_thread = Thread(target = hub.hub).start()
