#!/usr/bin/env python
# -*- coding:utf-8 -*-
# used  for python3.*
# import _thread
import random
import socket


def testport(port):
    url = '127.0.0.1'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((url, int(port)))
        s.shutdown(2)
        # 利用shutdown()函数使socket双向数据传输变为单向数据传输。shutdown()需要一个单独的参数，
        # 该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写。
        return True
    except:
        return False


def findport():
    find = False
    port = random.randint(40000, 50000)
    while find:
        if testport(port):
            find = True
        else:
            port = random.randint(40000, 50000)
    return port
