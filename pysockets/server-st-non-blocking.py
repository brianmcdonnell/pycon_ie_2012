#!/usr/bin/env python
import socket
import time
s0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s0.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s0.setblocking(0)
s0.bind(('', 8888))
s0.listen(10)

def handle_request(s1):
    str_buf = ''
    end_of_request = False

    while not end_of_request:
        str_buf += s1.recv(8)
        if str_buf.strip().endswith('.'):
            end_of_request = True
    #s1.send(str_buf.upper())

socket_list = []
while True:
    try:
        s1, _ = s0.accept()
        s1.setblocking(0)
        socket_list.append(s1)
    except socket.error as err:
            print "No new connections"

    for n, sn in enumerate(socket_list):
        try:
            handle_request(sn)
        except socket.error as err:
            print "%s: Nothing to read" % n

    time.sleep(0.5)


