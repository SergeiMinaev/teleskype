#!/usr/bin/env python
import signal
import sys
import telegram_connector


def ctrl_c_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)


telegram_connector.run()
