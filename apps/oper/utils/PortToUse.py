#!/usr/bin/env python
# -*- coding:utf-8 -*-
# used  for python3.*
# import _thread
import random
import socket
import time

socket.setdefaulttimeout(3)  # 设置默认超时时间


def testport(port):
    # url = input('Input the ip you want to scan: ')
    url = '127.0.0.1'
    # lock = _thread.allocate_lock()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((url, port))
    if result == 0:
        return False
    else:
        return True


def findport():
    find = False
    port = random.randint(40000, 50000)
    while find:
        if testport(port):
            find = True
        else:
            port = random.randint(40000, 50000)
    return port
