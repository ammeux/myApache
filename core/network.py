import socket
import threading
import datetime
import os
import sys

from env import ROOTPATH
from api import parse_request, HTTPResponse, format_response, parse_php_response, HTTPDuplex
from core.core import *

def handler(conn, addr, addonsList):
    data = conn.recv(1024).decode('utf8').rstrip()
    if not data:
        conn.close()
    parsed_request = parse_request(data)

    duplex = HTTPDuplex()
    duplex.request = parsed_request
    duplex.socket = conn

    for launchAddon in addonsList:
        launchedAddon = launchAddon()
        launchedAddon.execute(duplex)

    if duplex.response:
        conn.send(duplex.response)
        conn.close()

class ApacheNetwork(object):

    def __init__(self, addonsList, host, port):
        self.addonsList = addonsList
        self.host = host
        self.port = port

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(1)
        while True:
            print("listen to port {} at {}".format(self.port, datetime.datetime.now()))
            conn, addr = sock.accept()
            ip, port = str(addr[0]), str(addr[1])
            print("receive from port {} at ip {}".format(port, ip))
            connThread = threading.Thread(target = handler, args=(conn, addr, self.addonsList)).start()