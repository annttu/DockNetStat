#!/usr/bin/env python
# encoding: utf-8

import unittest
import multiprocessing
import time

from src import ping, udp, tcp, docknetstat_server

class TestPing(unittest.TestCase):
    def setUp(self):
        self.ping = ping.Ping()

    def test_ping_localhost(self):
        self.assertTrue(self.ping.is_alive('127.0.0.1'), "Ping to localhost should success")

    def test_ping_unreachable(self):
        self.assertFalse(self.ping.is_alive('255.255.255.254'), "Ping to unavailable address should fail")


class TestUdp(unittest.TestCase):
    def setUp(self):
        self.udp = udp.Udp('127.0.0.1', 12345)
        self.server = docknetstat_server.Server('127.0.0.1', 12345)

    def test_udp_server_not_running(self):
        self.assertFalse(self.udp.test(), "Udp test to unreachable port should fail")

    def test_udp_server_running(self):
        process = multiprocessing.Process(self.server.run, args=())
        process.start()
        time.sleep(2)
        self.assertTrue(self.udp.test(), "Udp test to reachable port should success")
        process.shutdown()


class TestTcp(unittest.TestCase):
    def setUp(self):
        self.tcp = tcp.Tcp('127.0.0.1', 12346)
        self.server = docknetstat_server.Server('127.0.0.1', 12346)

    def test_udp_server_not_running(self):
        self.assertFalse(self.tcp.test(), "Tcp test to unreachable port should fail")

    def test_udp_server_running(self):
        process = multiprocessing.Process(self.server.run, args=())
        process.start()
        time.sleep(2)
        self.assertTrue(self.tcp.test(), "Tcp test to reachable port should success")
        process.shutdown()


if __name__ == "__main__":
    unittest.main()
