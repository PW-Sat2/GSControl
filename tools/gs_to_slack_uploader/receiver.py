import time
import zmq
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(
    __file__), '../../build/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(
    __file__), '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from radio.radio_frame_decoder import *
decoder = response_frames.FrameDecoder(response_frames.frame_factories)
from utils import ensure_string, ensure_byte_list

class Receiver:
    def __init__(self, target="localhost", port=7001):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.SUB)
        self.sock.connect("tcp://%s:%d" % (target, port))
        self.sock.setsockopt(zmq.SUBSCRIBE, "")
        self.set_timeout(-1)
        self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)

    """Set timeout on socket.
        -1 for infinity"""
    def set_timeout(self, timeout_in_ms=-1):
        self.sock.setsockopt(zmq.RCVTIMEO, timeout_in_ms)

    class TimeoutError(Exception):
        pass

    """ Receive RAW frame from socket. If timeout expired zmq.Again is raised """
    def receive_raw(self):
        return self.sock.recv()

    def get_packet(self):
        frame_data = self.receive_raw()
        return {'timestamp': time.time(), 'frame': self.parse_packet(frame_data)}

    def parse_packet(self, frame_data):
        return decoder.decode(ensure_byte_list(frame_data[16:-2]))
