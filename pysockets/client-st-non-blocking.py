#!/usr/bin/env python
import socket
import select
import datetime

#raw_request = '''GET /static/base/images/logo.png HTTP/1.1\r
#raw_request = '''GET /no_content HTTP/1.1\r
raw_request = '''GET /empty_gif HTTP/1.1\r
Host: loadtest.blockmetrics.com\r
User-Agent: loadtest(simple evented test)\r
Connection: close\r
\r
'''

# End of line
EOL = '\r\n'
# End of header
EOH = EOL*2

epoll = select.epoll()

class Reactor(object):

    def __init__(self):
        self.request_count = 0
        self.connections = {}
        self.requests = {}
        self.responses = {}

    def open_connection(self):
        host, port = 'loadtest.blockmetrics.com', 80
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.setblocking(0)
        #sck.connect_ex(('loadtest.blockmetrics.com', 80))
        sck.connect_ex((host, port))
        fileno = sck.fileno()
        self.connections[fileno] = sck
        self.requests[fileno] = raw_request
        self.responses[fileno] = ''
        epoll.register(fileno, select.EPOLLOUT)

    def close_connection(self, sck):
        fileno = sck.fileno()
        sck.close()
        del self.connections[fileno]
        del self.requests[fileno]
        del self.responses[fileno]
        epoll.unregister(fileno)

    def request_complete(self, result):
        status, cookies = result
        if status not in [200, 204, 301, 302]:
            print "Bad status: %s" % status
        self.request_count += 1
        if self.request_count % 100 == 0:
            now = datetime.datetime.utcnow()
            seconds = (now - self.start_time).seconds
            if seconds > 0:
                print "req: %s\tsec: %s\treq/sec: %s\tcli: %s" % (self.request_count, seconds, self.request_count / float(seconds), len(self.connections))

    def run(self):
        self.start_time = datetime.datetime.utcnow()
        running = True
        try:
            while running:
                events = epoll.poll(1)

                for fileno, event in events:

                    if event & select.EPOLLOUT:
                        byteswritten = self.connections[fileno].send(self.requests[fileno])
                        self.requests[fileno] = self.requests[fileno][byteswritten:]
                        if len(self.requests[fileno]) == 0:
                            epoll.modify(fileno, select.EPOLLIN)
                            #print "Request sent"

                    elif event & select.EPOLLIN:
                        self.responses[fileno] += self.connections[fileno].recv(1024)
                        response = self.responses[fileno]
                        # Check for the complete header response
                        if EOH in response:
                            headers = response.split(EOH)[0]
                            header_len = len(headers) + len(EOH)
                            hdr_dict = {}
                            headers = headers.split(EOL)
                            # Parse first line of response
                            first_line = headers[0]
                            http_ver = first_line[:8]
                            status_code = int(first_line[9:12])
                            status_msg = first_line[13:]
                            headers = headers[1:]
                            # Stick the headers in a dictionary
                            for header_line in headers:
                                lhs, rhs = header_line.split(': ')
                                hdr_dict[lhs.strip().lower()] = rhs
                            content_len = None
                            if status_code == 204:
                                content_len = 0
                            else:
                                content_len = hdr_dict.get('content-length', None)
                            if content_len is not None:
                                content_len = int(content_len)
                            else:
                                raise Exception("'Content-Length' header required.")
                            # Check 
                            total_len = header_len + content_len
                            remaining = total_len - len(response)
                            if remaining == 0:
                                #print "---"
                                #print self.responses[fileno]
                                #print "___"
                                #running = False
                                self.close_connection(self.connections[fileno])
                                self.open_connection()
                                self.request_complete((status_code, None))

                    elif event & select.EPOLLHUP:
                        print "HUP"
                        self.close_connection(self.connections[fileno])

            while True:
                import time
                print "sleeping"
                time.sleep(4)

        finally:
            epoll.close()

def main():
    import sys
    num_clients = int(sys.argv[1])
    reactor = Reactor()
    for i in range(num_clients):
        reactor.open_connection()
    reactor.run()

if __name__ == '__main__':
    main()
