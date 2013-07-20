# encoding: utf-8

import threading
from time import sleep


class StatModule(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = False

    def stop(self):
        self._stop = True

    def update(self):
        pass

    def run(self):
        while not self._stop:
            self.update()
            sleep(2)
