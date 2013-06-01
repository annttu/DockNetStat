#!/usr/bin/env python
# encoding: utf-8

import logging
import socket
import signal



logger = logging.getLogger('Tcp')

def timeout_handler(signum, frame):
    logger.debug("Timeout occured")


class Tcp(object):
    def __init__(self, host, port, msg='ECHO ME SOMETHING\n'):
        self.host = host
        self.port = port
        self.echo_msg = msg

    def test(self):
        """
        Test if connection is working
        """
        got_retval = False
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((self.host, self.port))
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(3)
        tcp_socket.send(self.echo_msg)
        while True:
            try:
                recv_data = tcp_socket.recv(2048)
            except socket.error as e:
                logger.info("TCP Timeout")
                break
            if recv_data == self.echo_msg:
                got_retval = True
                break
            else:
                logger.error("Got unexcepted respond \"%s\"" % recv_data)
        signal.alarm(0)
        tcp_socket.close()
        return got_retval

if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    s = Tcp('127.0.0.1', 12345)
    if s.test():
        print("Tcp is working")
    else:
        print("Tcp is not working")
