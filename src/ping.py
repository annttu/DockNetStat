#!/usr/bin/env python
# encoding: utf-8

# This file is part of DockNetStat project
# Author: Antti Jaakkola
# Annttu (at) docnetstat (dot) annttu (dot) (finland tld)

import sys
import os
from subprocess import Popen, PIPE
import logging

logger = logging.getLogger('Ping')

_PING = '/sbin/ping'

class Ping(object):
    def __init__(self):
        pass

    def _parse_ping(self, row):
        # Request timeout for icmp_seq 1047
        # 64 bytes from 8.8.8.8: icmp_seq=1045 ttl=47 time=14068.099 ms
        if 'time=' in row and 'icmp_seq=' in row:
            ret = {}
            try:
                row = row.split()
                return {
                 'alive' : True,
                 'target': str(row[3][:-1]),
                 'icmp_seq' : int(row[4].split("=")[1]),
                 'ttl' : int(row[5].split("=")[1]),
                 'time' : float(row[6].split("=")[1])
                }
            except ValueError as e:
                logger.exception(e)
                return None
        elif "timeout" in row:
            seq = int(row.split()[-1])
            return {'alive' : False, 'error' : 'timeout', 'icmp_seq' : seq}
        elif "No route to host":
            return {'alive' : False, 'error' : 'no route to host'}
        else:
            logger.error("Unknown ping row \"%s\"" % row)
            return None

    def _ping(self, host, count=3, interface=None, source_address=None):
        """
        Ping host,
        return dict containing ttl and time information
        """
        if 'PING' in os.environ:
            ping_cmd = os.environ['PING']
        else:
            ping_cmd = _PING
        args = [ping_cmd, '-nc', str(count)]
        if interface:
            args.append('-b')
            args.append(str(interface))
        if source_address:
            args.append('-S')
            args.append(str(source_address))
        args.append(host)
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

    def ping(self, *args, **kwargs):
        for ping in self._ping(*args, **kwargs):
            if 'alive' in ping:
                if ping['alive']:
                    return ping
        return {'alive': False}

    def is_alive(self, *args, **kwargs):
        for ping in self._ping(*args, **kwargs):
            if 'alive' in ping:
                if ping['alive']:
                    return True
        return False

if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    p = Ping()
    ret = p.ping('8.8.8.8')
    if ret['alive']:
        print("8.8.8.8 is alive, time: %s" % ret['time'])
    else:
        print("8.8.8.8 is not alive")
