#!/usr/bin/env python
# encoding: utf-8

from src.docknetstat_server import Server
import argparse
import logging

logger = logging.getLogger()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='DockNetStat Server')
    parser.add_argument('--address', dest='address', type=str,
                       help='Address to bind server', default="127.0.0.1")
    parser.add_argument('--port', type=int, default="12345",
                       help='Port to bind server tcp and udp')
    parser.add_argument('--debug', action='store_true', default=False,
                        help="Debug")
    args = parser.parse_args()
    logging.basicConfig()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
    Server(args.address, args.port).main()
