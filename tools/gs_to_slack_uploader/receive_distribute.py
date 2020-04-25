from threading import Thread, Event
import sys
import os

from receiver import Receiver
import logging
import traceback


class ReceiveDistribute(Thread):
    def __init__(self, rx_queue):
        Thread.__init__(self)
        self.rcv = Receiver()
        self.rcv.set_timeout(1000)
        self.rx_queue = rx_queue
        self._stop_event = Event()
        self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)

    def stop(self):
        self._stop_event.set()

    def run(self):
        self.logger.log(logging.INFO, "Starting ReceiveDistribute")
        while not self._stop_event.is_set():
            packet = self.rcv.get_packet()
            if packet is not None:
                self.logger.log(logging.DEBUG, packet)
                self.rx_queue.append(packet)
        self.logger.log(logging.INFO, "Finished ReceiveDistribute")
