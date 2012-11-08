#!/usr/bin/env python
import socket
sck_lstn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck_lstn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sck_lstn.bind(('', 8888))
sck_lstn.listen(10)

def handle_request(sck_new):
    str_buf = ''
    end_of_request = False

    while not end_of_request:
        str_buf += sck_new.recv(8) # BLOCKING
        if str_buf.strip().endswith('.'):
            end_of_request = True
    sck_new.send(str_buf.upper()) # BLOCKING

while True:
    sck_new, addr = sck_lstn.accept() # BLOCKING
    handle_request(sck_new)
