#!/usr/bin/python

import time
import json

from ktaneparser.ktaneparser import KTANEParser


if __name__ == '__main__':

    with open('config.json') as config_file:
        config_data = json.load(config_file)

    log_file = config_data["files"]["ktane_log_file"]
    state_file = config_data["files"]["status_file"]
    modules_file = config_data["files"]["modules_file"]
    defused_file = config_data["files"]["defused_file"]

    success_messages = config_data["messages"]["success"]
    failure_messages = config_data["messages"]["failure"]

    print 'log_file = {}'.format(log_file)
    print 'state_file = {}'.format(state_file)
    print 'modules_file = {}'.format(modules_file)
    print 'defused_file = {}'.format(defused_file)

    p = KTANEParser(state_file, modules_file, defused_file, success_messages, failure_messages)
    f = open(log_file, 'r')
    while True:
        line = ''
        while len(line) == 0 or line[-1] != '\n':
            tail = f.readline()
            if tail == '':
                time.sleep(0.1)
                continue
            line += tail
        p.handle_line(tail)
