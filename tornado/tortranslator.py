import socket

import tornado.iostream
import tornado.ioloop
import tornado.web

class TorTranslator(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.callback = None
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = tornado.iostream.IOStream(s)
        self.stream.set_close_callback(self.close_callback)

    def translate(self, input_str, callback=None):
        self.data = input_str
        self.callback = callback
        self.stream.connect((self.host, self.port), self.send_translation_data)

    def send_translation_data(self, *args, **kwargs):
        self.stream.write(str(self.data))
        # Our only protocol rule
        self.stream.read_until('.', self.translation_complete)

    def translation_complete(self, translated_data):
        self.stream.close()
        if self.callback:
            self.callback(translated_data)

    def close_callback(self, *args, **kwargs):
        if self.error:
            self.callback(None)

    @property
    def error(self):
        return self.stream.error
