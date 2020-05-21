#!/usr/bin/env python3

# TODO: This is quick and dirty and need way more error handling. Starting with try catching the db connection...

import re
import sqlite3
import requests
import os
import sys
from datetime import datetime

DEBUG = len(sys.argv) > 1 && sys.argv[1] == "--debug"
if not DEBUG:
    PIHOLE_DB = '/etc/pihole/gravity.db'
else:
    PIHOLE_DB = "./gravity.db"
DEFAULT_MASTER_LIST = '/etc/pihole-cname-master.list'
USER_MASTER_LIST = './pihole-cname-master.list'
# If we execute this from something like cron we don't want ANSI control character
USE_COLOR = sys.stdout.isatty()

if USE_COLOR:
    ANSI_GREEN = '\033[92m'
    ANSI_RED = '\033[91m'
    ANSI_END = '\033[0m'
else:
    ANSI_GREEN = ''
    ANSI_RED = ''
    ANSI_END = ''

COMMENT_PATTERN = r'#.*'
SQL_STATEMENT = "INSERT OR IGNORE INTO domainlist (type, domain, enabled, comment) VALUES (3, ?, 1, ?);"


def unix():
    return os.name == 'unix'


def root():
    if unix():
        return os.getuid() == 0
    else:  # I assume you are smart enough not to be always admin on windows
        return True


def endscript(code=None):
    try:
        if code is not None:
            exit(code)
        else:
            print(f"> Import finished @ {str(datetime.now())}")
            exit()
    except SystemExit:
        pass  # Yeah.. we kinda thought this would happen


def locate_masterlist():
    if os.path.exists(DEFAULT_MASTER_LIST):
        print(f"> Using system master list [{DEFAULT_MASTER_LIST}]")
        return DEFAULT_MASTER_LIST
    elif os.path.exists(USER_MASTER_LIST):
        print(f"> Using user master list [{USER_MASTER_LIST}]")
        return USER_MASTER_LIST
    else:
        print(
            f"> No master list found. Please either create {DEFAULT_MASTER_LIST} or put {USER_MASTER_LIST} next to this script")
        endscript(1)


def import_cnames(master):
    print(
        f"\t> Fetching new cname entries from {ANSI_GREEN}{master}{ANSI_END}")

    response = requests.get(master)
    if not response.ok:
        print(
            f"\t> Failed to fetch {ANSI_GREEN}{master}{ANSI_END}! HTTP Code: {ANSI_RED}{response.status_code}{ANSI_END}")
        return
    else:
        print(
            f"\t> Received OK {ANSI_GREEN}({response.status_code}){ANSI_END} from server")

    print("\t> Filtering response...")
    domainlist = filter(lambda l: l != '', re.sub(
        COMMENT_PATTERN, '', response.text).splitlines())

    print("\t> Opening PiHole gravity.db...")
    now = datetime.now()
    comment = f'Auto Import - {str(now)}'
    # Creating the list of sanitised entries
    data = map(lambda x: (x, comment), domainlist)
    db = sqlite3.connect(PIHOLE_DB)
    cursor = db.cursor()
    print("\t> Importing new entries...")
    cursor.executemany(SQL_STATEMENT, data)
    db.commit()
    print(
        f"\t> Found and imported {ANSI_GREEN}{cursor.rowcount}{ANSI_END} entries from {ANSI_GREEN}{master}{ANSI_END}")
    db.close()


if not root():
    print(f"> {ANSI_RED}This script needs to be run as an administrator{ANSI_END}")
    endscript(1)

masterlist_path = locate_masterlist()
with open(masterlist_path, 'r') as masterlist:
    entries = masterlist.readlines()
    for entry in entries:
        import_cnames(entry)
endscript()
