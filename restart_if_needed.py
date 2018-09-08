#!/usr/bin/env python

"""
Checks teleskype's connection status. Restart teleskype if status is not online.
Keep this script in main teleskype's directory.
"""
import os
import subprocess
import signal
import configparser
from time import sleep
from datetime import datetime


config = configparser.ConfigParser()
config.read('config.ini')
python_path = config['main']['python_path']


def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def get_bot_pid():
    bot_pid = None
    try:
        f = open('pid.txt', 'r')
        bot_pid = int(f.read())
    except:
        print("Can't get PID from pid.txt")
    return bot_pid


def is_need_restart():
    telegram_status = open('telegram_status.txt').read()
    skype_status = open('skype_status.txt').read()
    telegram_mtime = os.path.getmtime('telegram_status.txt')
    skype_mtime = os.path.getmtime('skype_status.txt')
    now = datetime.now().timestamp()
    if now - telegram_mtime > 60 or now - skype_mtime > 60:
        print('Something goes wrong: status files were updated too long ago.')
        return True
    if telegram_status == 'error' or skype_status == 'error':
        print('Something goes wrong: some of status files contain error message.')
        return True
    return False


def restart():
    print('Trying to restart teleskype')
    os.chdir(os.path.dirname(__file__))
    bot_pid = get_bot_pid()

    if bot_pid:
        if check_pid(bot_pid):
            os.kill(bot_pid, signal.SIGTERM)
            sleep(1)
            if check_pid(bot_pid):
                print("Can't kill PID with SIGTERM. Using SIGKILL")
                os.kill(bot_pid, signal.SIGKILL)
                sleep(1)
            else:
                print(f"PID {bot_pid} was terminated successfully")
        else:
            print(f"PID {bot_pid} doesn't exist")

        if not check_pid(bot_pid):
            print("Starting teleskype")
            subprocess.Popen(["nohup", "./teleskype.py"],
                     stdout=open('/dev/null', 'w'),
                     stderr=open('logfile.log', 'a'),
                     preexec_fn=os.setpgrp)
            sleep(0.5)
            bot_pid = get_bot_pid()
            if bot_pid:
                if check_pid(bot_pid):
                    print("Teleskype started successfully")
                else:
                    print("Error: failed to start teleskype")
            else:
                print("Can't get PID of new teleskype process. Can't check if it started successfully")
        else:
            print("Still can't kill PID. Giving up")

if is_need_restart():
    restart()
else:
    print("All fine")
