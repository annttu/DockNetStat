#!/usr/bin/env python
# encoding: utf-8

from src.ping import Ping
from src.tcp import Tcp
from src.udp import Udp

import os

# Apple stuff
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

UPDATE_INTERVAL=5

start_time = NSDate.date()

def hide_from_dock():
    """hide icon from dock"""
    NSApplicationActivationPolicyRegular = 0
    NSApplicationActivationPolicyAccessory = 1
    NSApplicationActivationPolicyProhibited = 2
    NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)

class DocNetStatDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):

        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.statusImage = NSImage.alloc()
        icon = os.path.join(os.path.dirname(os.path.abspath(__file__)),'images/OK-32.png')
        self.statusImage.initWithContentsOfFile_(icon)
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
        self.udp_status.setTitle_("TCP status")
        self.udp_status.setToolTip_("Status of TCP-connections")
        self.udp_status.setKeyEquivalent_('t')
        self.menu.addItem_(self.udp_status)

        # Sync and Quit buttons

        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Sync...', 'sync:', '')
        self.menu.addItem_(menuitem)

        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
        self.menu.addItem_(menuitem)
        self.statusItem.setMenu_(self.menu)
        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
            start_time, float(UPDATE_INTERVAL), self, 'sync:', None, True)


        # Initialize Ping, Tcp and Udp

        self.udp = Udp('217.30.184.184', 61956)
        self.tcp = Tcp('217.30.184.184' ,61956)
        self.ping = Ping()


        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
        self.timer.fire()
        NSLog("DocNetStat started!")


    def sync_(self, notification):
        if self.tcp.test():
            self.tcp_status.setTitle_('TCP Ok')
        else:
            self.tcp_status.setTitle_('TCP Error')
        if self.udp.test():
            self.udp_status.setTitle_('UDP Ok')
        else:
            self.udp_status.setTitle_('UDP Error')
        ret = self.ping.ping("217.30.184.184")
        if ret['alive']:
            self.ping_status("Ping: %s" % ret['time'])
        else:
            self.ping_status("Ping Error")

if __name__ == "__main__":
    try:
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
