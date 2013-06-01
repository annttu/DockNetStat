#!/usr/bin/env python
# encoding: utf-8

"""
DockNetStat server

Server is used to test udp and tcp connections
"""

import socket
import signal
import logging
import threading
import time
import select

logger = logging.getLogger('DockNetStat')

def timeout_handler(signum, frame):
    logger.info("Timeout occured in %s" % (frame,))
    return

class SocketError(Exception):
    pass

class ProtoServer(threading.Thread):
    name = 'Protoserver'
    def __init__(self, host, port, *args, **kwargs):
        super(ProtoServer, self).__init__(*args, **kwargs)
        self.port = port
        self.host = host
        self.echo_message = u"ECHO ME SOMETHING"
        self.connections = []
        self._stop = False
        self.socket = None
        self.open_socket()

    def open_socket(self):
        """
        Open self.socket
        """
        pass

    def kill(self):
        self._stop = True

    def handle_new(self):
        pass

    def handle_current(self, s):
        pass

    def msg_valid(self, msg):
        return msg.strip("\n").strip() == self.echo_message

    def handle_closing(self, s):
        s.close()
        for i in xrange(len(self.connections)):
            if self.connections[i] == x:
                self.connections.pop(i)
                return True
        return False

    def close(self):
        logger.info("Closing %s" % self.name)
        if not self.socket:
            return
        try:
            self.socket.close()
        except Exception as e:
            logger.exception(e)

    def run(self):
        while not self._stop:
            readers = [self.socket] + self.connections
            writers = []
            excepts = readers
            rlist, wlist, xlist = select.select(readers, writers, excepts, 1)
            for reader in rlist:
                if reader == self.socket:
                    try:
                        self.handle_new()
                    except SocketError as e:
                        logger.exception(e)
                        logger.error("Socket failed, closing connection")
                        self.close()
                        return
                else:
                    self.handle_current(reader)
            for x in xlist:
                if self.socket == x:
                    logger.error("Server socket trow exception, stopping server")
                    return
                else:
                    self.handle_closing(x)
        self.close()


class TCPServer(ProtoServer):
    name = 'TCPServer'
    def open_socket(self):
        if self.socket:
            return
        logger.info("Opened tcp socket at %s:%s" % (self.host, self.port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)

    def handle_new(self):
        #signal.signal(signal.SIGALRM, timeout_handler)
        #signal.alarm(5)
        sock, addr = self.socket.accept()
        logger.info("New connection from %s:%s" % addr)
        data = sock.recv(2048)
        if self.msg_valid(data):
            sock.send(self.echo_message + '\n')
        else:
            logger.error("Invalid data \"%s\" received from %s:%s" % (data, addr[0], addr[1]))
        sock.close()
        #signal.alarm(0)

class UDPServer(ProtoServer):
    name = 'UDPServer'
    def open_socket(self):
        if self.socket:
            return
        logger.info("Opened udp socket at %s:%s" % (self.host, self.port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

    def handle_new(self):
        #signal.signal(signal.SIGALRM, timeout_handler)
        #signal.alarm(5)
        data, addr = self.socket.recvfrom(2048)
        logging.info("New connection from %s:%s" % addr)
        if self.msg_valid(data):
            self.socket.sendto(self.echo_message + '\n', addr)
        #signal.alarm(0)

class Server(object):
    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.udp_server = UDPServer(self.host, self.port)
        self.tcp_server = TCPServer(self.host, self.port)

    def exit(self):
        for i in [self.udp_server, self.tcp_server]:
            i.kill()

    def main(self):
        self.udp_server.start()
        self.tcp_server.start()
        try:
            while True:
                if not self.udp_server.is_alive():
                    self.udp_server = UDPServer(self.host, self.port)
                    self.udp_server.start()
                    logger.error("UDPServer was dead, respawned!")
                if not self.tcp_server.is_alive():
                    self.tcp_server = TCPServer(self.host, self.port)
                    self.tcp_server.start()
                    logger.error("TCPServer was dead, respawned!")
                time.sleep(5)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logger.exception(e)
        except:
            pass
        self.exit()

if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    Server('127.0.0.1', 12345).main()
