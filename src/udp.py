#!/usr/bin/env python
# encoding: utf-8

import logging
import socket
import signal



logger = logging.getLogger('Udp')

def timeout_handler(signum, frame):
    logger.debug("Timeout occured")


class Udp(object):
    def __init__(self, host, port, msg='ECHO ME SOMETHING\n'):
        self.host = host
        self.port = port
        self.echo_msg = msg

    def test(self):
        """
        Test if connection is working
        """
        got_retval = False
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(3)
        udp_socket.sendto(self.echo_msg, (self.host, self.port))
        while True:
            try:
                recv_data, addr = udp_socket.recvfrom(2048)
            except socket.error as e:
                logger.info("UDP Timeout")
                break
            if addr[0] != self.host:
                logger.error("Got reply to udp message from unknown host %s" % (addr,))
                continue
            if recv_data == self.echo_msg:
                got_retval = True
                break
            else:
                logger.error("Got unexcepted respond \"%s\"" % recv_data)
        signal.alarm(0)
        udp_socket.close()
        return got_retval

if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    s = Udp('127.0.0.1', 12345)
    if s.test():
        print("Udp is working")
    else:
        print("Udp is not working")
