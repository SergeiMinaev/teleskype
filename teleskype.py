#!/usr/bin/env python
import signal
import sys
from threading import Thread
import telegram_connector
import skype_connector

def ctrl_c_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)


skype_thread = Thread(target = skype_connector.run).start()
telegram_thread = Thread(target = telegram_connector.run).start()
