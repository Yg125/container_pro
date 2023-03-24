# #!/usr/bin/env python
# # -*- coding:utf-8 -*-
# # used  for python3.*
# # import _thread
# import random
# import socket
#
#
# def testport(port):
#     # url1 = '219.223.251.94'
#     url2 = '219.223.251.95'
#     url3 = '219.223.251.96'
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # try:
#     #     s.connect((url1, int(port)))
#     #     s.shutdown(2)
#     # except:
#     #     return False
#     try:
#         s.connect((url2, int(port)))
#         s.shutdown(2)
#         return True
#     except:
#         return False
#     # try:
#     #     s.connect((url3, int(port)))
#     #     s.shutdown(2)
#     # except:
#     #     return False
#         # 利用shutdown()函数使socket双向数据传输变为单向数据传输。shutdown()需要一个单独的参数，
#         # 该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写。
#     # return True
#
#
#
# def findport():
#     port = random.randint(40000, 50000)
#     while testport(port):
#         port = random.randint(40000, 50000)
#     return port
import os
import random


def testport(port):
    result1 = os.popen('ssh Myserver95 lsof -i:' + str(port)).read().split()
    result2 = os.popen('ssh Myserver96 lsof -i:' + str(port)).read().split()
    result3 = os.popen('ssh Myserver94 lsof -i:' + str(port)).read().split()
    if len(result1) == 0 and len(result2) == 0 and len(result3) == 0:  # 该端口没有被占用
        return True
    else:
        return False


def findport():
    port = random.randint(40000, 50000)
    while not(testport(port)):
        port = random.randint(40000, 50000)
    return port
