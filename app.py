#!/usr/bin/env python
# encoding: utf-8

import os
import sys

d = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, d)

from src.ping import Ping
from src.tcp import Tcp
from src.udp import Udp

import logging

# Apple stuff
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

UPDATE_INTERVAL = 5
PING_INTERVAL = 2

start_time = NSDate.date()
ping_start_time = NSDate.date()


def hide_from_dock():
    """hide icon from dock"""
    #NSApplicationActivationPolicyRegular = 0
    #NSApplicationActivationPolicyAccessory = 1
    NSApplicationActivationPolicyProhibited = 2
    NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)


class DocNetStatDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):

        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength)
        self.statusImage = NSImage.alloc()

        self.error = False
        # Icons
        mydir = os.path.dirname(os.path.abspath(__file__))
        self.ok_icon = os.path.join(mydir, 'images/OK.png')
        self.tcp_icon = os.path.join(mydir, 'images/TCP-red.png')
        self.udp_icon = os.path.join(mydir, 'images/UDP-red.png')
        self.error_icon = os.path.join(mydir, 'images/ERROR-red.png')
        self.statusImage.initWithContentsOfFile_(self.ok_icon)
        self.statusItem.setImage_(self.statusImage)
        self.statusItem.setToolTip_('NetStat')
        self.statusItem.setHighlightMode_(TRUE)
        self.statusItem.setEnabled_(TRUE)

        # Menu
        self.error = True
        self.menu = NSMenu.alloc().init()
        # Ping
        self.ping_status = NSMenuItem.alloc().init()
        self.ping_status.setTitle_("Ping time")
        self.ping_status.setToolTip_("Ping time")
        self.ping_status.setKeyEquivalent_('p')
        self.menu.addItem_(self.ping_status)

        # Tcp
        self.tcp_status = NSMenuItem.alloc().init()
        self.tcp_status.setTitle_("TCP status")
        self.tcp_status.setToolTip_("Status of TCP-connections")
        self.tcp_status.setKeyEquivalent_('t')
        self.menu.addItem_(self.tcp_status)

        # Udp
        self.udp_status = NSMenuItem.alloc().init()
        self.udp_status.setTitle_("UDP status")
        self.udp_status.setToolTip_("Status of UDP-connections")
        self.udp_status.setKeyEquivalent_('u')
        self.menu.addItem_(self.udp_status)

        # Sync and Quit buttons

        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Sync...', 'syncall:', '')
        self.menu.addItem_(menuitem)

        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Quit', 'terminate:', '')
        self.menu.addItem_(menuitem)
        self.statusItem.setMenu_(self.menu)
        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
            start_time, float(UPDATE_INTERVAL), self, 'sync:', None, True)
        self.ping_timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
            ping_start_time, float(PING_INTERVAL), self, 'pingsync:', None, True)

        # Initialize Ping, Tcp and Udp

        self.udp = Udp('217.30.184.184', 61956)
        self.tcp = Tcp('217.30.184.184', 61956)
        self.ping = Ping('217.30.184.184')
        self.ping.start()

        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer,
                                                     NSDefaultRunLoopMode)
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.ping_timer,
                                                     NSDefaultRunLoopMode)
        self.timer.fire()
        self.ping_timer.fire()
        NSLog("DocNetStat started!")

    def syncall_(self, notification):
        self.pingsync_(notification)
        self.sync_(notification)

    def pingsync_(self, notification):
        ret = self.ping.ping()
        if ret['alive']:
            self.ping_status.setTitle_("Ping: %s" % ret['time'])
            self.statusItem.setTitle_(u"%2.1fms" % ret['time'])
        else:
            self.ping_status.setTitle_("Ping Error")
            self.statusItem.setTitle_(u"E")

    def sync_(self, notification):
        tcp_error = False
        udp_error = False
        if self.tcp.test():
            self.tcp_status.setTitle_('TCP Ok')
        else:
            self.tcp_status.setTitle_('TCP Error')
            tcp_error = True
        if self.udp.test():
            self.udp_status.setTitle_('UDP Ok')
        else:
            udp_error = True
            self.udp_status.setTitle_('UDP Error')

        if tcp_error or udp_error:
            if not self.error:
                self.error = True
            if not tcp_error and udp_error:
                self.statusImage.initWithContentsOfFile_(self.udp_icon)
            elif tcp_error and not udp_error:
                self.statusImage.initWithContentsOfFile_(self.tcp_icon)
            else:
                self.statusImage.initWithContentsOfFile_(self.error_icon)
        elif self.error:
            self.statusImage.initWithContentsOfFile_(self.ok_icon)

    def applicationShouldTerminate_(self, notification):
        if self.ping.is_alive():
            self.ping.stop()
            self.ping.join()
        return 1

if __name__ == "__main__":
    try:
        logging.basicConfig()
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        app = NSApplication.sharedApplication()
        app.hide_(TRUE)
        delegate = DocNetStatDelegate.alloc().init()
        app.setDelegate_(delegate)
        hide_from_dock()
        AppHelper.runEventLoop()
    except KeyboardInterrupt:
        delegate.terminate_()
        AppHelper.stopEventLoop()
        pass
