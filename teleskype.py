#!/usr/bin/env python
import signal
import sys
import os
import logging
from threading import Thread
import telegram_connector
import skype_connector
import hub
from models import db, Bridge
from common import init_loc


def ctrl_c_handler(sig, frame):
    db.close()
    sys.exit(0)


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Bridge])


def init_logging():
    logging.basicConfig(
            filename="teleskype.log",
            filemode="w",
            format='%(asctime)s %(message)s')


def save_pid():
    mypid = os.getpid()
    f = open('pid.txt', 'w')
    f.write(str(mypid))
    f.close()


signal.signal(signal.SIGINT, ctrl_c_handler)
init_db()
init_loc()
init_logging()
save_pid()

skype_thread = Thread(target = skype_connector.run).start()
telegram_thread = Thread(target = telegram_connector.run).start()
hub_thread = Thread(target = hub.hub).start()
