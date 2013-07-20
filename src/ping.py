#!/usr/bin/env python
# encoding: utf-8

# This file is part of DockNetStat project
# Author: Antti Jaakkola
# Annttu (at) docnetstat (dot) annttu (dot) (finlands tld)

import os
from subprocess import Popen, PIPE
import logging
from .utils import StatModule

logger = logging.getLogger('Ping')

_PING = '/sbin/ping'


class Ping(StatModule):
    def __init__(self, host, count=3, interface=None, source_address=None):
        super(Ping, self).__init__()
        self.host = host
        self.count = count
        self.interface = interface
        self.source_address = source_address
        self.status = {'alive': False}
        self._stop = False

    def stop(self):
        self._stop = True

    def _parse_ping(self, row):
        # Request timeout for icmp_seq 1047
        # 64 bytes from 8.8.8.8: icmp_seq=1045 ttl=47 time=14068.099 ms
        if not row:
            return None
        row = row.strip()
        if not row:
            return None
        if 'time=' in row and 'icmp_seq=' in row:
            try:
                row = row.split()
                return {
                    'alive': True,
                    'target': str(row[3][:-1]),
                    'icmp_seq': int(row[4].split("=")[1]),
                    'ttl': int(row[5].split("=")[1]),
                    'time': float(row[6].split("=")[1])
                }
            except ValueError as e:
                logger.exception(e)
                return None
        elif "timeout" in row:
            seq = int(row.split()[-1])
            return {'alive': False, 'error': 'timeout', 'icmp_seq': seq}
        elif "No route to host" in row:
            return {'alive': False, 'error': 'no route to host'}
        elif "packets transmitted" in row or "PING" in row:
            return None
        elif "ping statistics" in row or "round-trip" in row:
            return None
        else:
            logger.error("Unknown ping row \"%s\"" % row)
            return None

    def _ping(self, *args, **kwargs):
        """
        Ping host,
        return dict containing ttl and time information

        TODO: packet loss
        """
        if 'PING' in os.environ:
            ping_cmd = os.environ['PING']
        else:
            ping_cmd = _PING
        args = [ping_cmd, '-nc', str(self.count)]
        if self.interface:
            args.append('-b')
            args.append(str(self.interface))
        if self.source_address:
            args.append('-S')
            args.append(str(self.source_address))
        args.append(self.host)
        logger.debug("Running ping with arguments %s" % (args,))
        ping = Popen(args, stdout=PIPE, stderr=PIPE)
        logger.debug("Ping running as pid %s" % ping.pid)
        ## TODO: timeout for this
        ping.wait()
        for row in ping.stdout.readlines():
            logger.debug("Ping output \"%s\"" % row[:-1])
            ret = self._parse_ping(row)
            if ret:
                logging.debug("Ping retval %s" % (ret,))
                yield(ret)

    def update(self):
        is_alive=False
        for ping in self._ping():
            if 'alive' in ping:
                if ping['alive']:
                    self.status = ping
                    is_alive = True
        if not is_alive:
            self.status = {'alive': False}

    def ping(self, *args, **kwargs):
        return self.status

    def is_alive(self, *args, **kwargs):
        if self.status:
            return self.status['alive']

if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    p = Ping()
    ret = p.ping('8.8.8.8')
    if ret['alive']:
        print("8.8.8.8 is alive, time: %s" % ret['time'])
    else:
        print("8.8.8.8 is not alive")
