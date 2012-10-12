#!/usr/bin/env python
import socket
import sys

HOST = ''
PORT = 8888
BACKLOG_SIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(BACKLOG_SIZE)

print "Listening"

conn, addr = s.accept()
print 'Connected with ' + addr[0] + ':' + str(addr[1])
