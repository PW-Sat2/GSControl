import zmq
import pmt

from utils import ensure_byte_list
import response_frames as response_frames


class Receiver:
    def __init__(self):
        from config import config
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.SUB)
        self.sock.connect("tcp://%s:7001" % config['GS_HOST'])
        self.sock.setsockopt(zmq.SUBSCRIBE, "")
        self.set_timeout(-1)

    """Set timeout on socket.
        -1 for infinity"""
    def set_timeout(self, timeout_in_ms=-1):
        self.sock.setsockopt(zmq.RCVTIMEO, timeout_in_ms)

    class TimeoutError(Exception):
        pass

    """ Receive RAW frame from socket. If timeout expired zmq.Again is raised """
    def receive_raw(self):
        data = self.sock.recv()
        vector = pmt.u8vector_elements(pmt.cdr(pmt.deserialize_str(data)))
        frame = ''.join([chr(i) for i in vector])
        return self._decode_kiss(frame)

    """ Receive and parse OBC frame. If timeout expired zmq.Again is raised """
    def receive_frame(self):
        rcv = self.receive_raw()
        rcv = self._make_frame(rcv)
        return rcv

    @staticmethod
    def _decode_kiss(frame):
        frame = frame[16:-2]
        return ensure_byte_list(frame)

    @staticmethod
    def _make_frame(frame):
        frame_decoder = response_frames.FrameDecoder(response_frames.frame_factories)
        return frame_decoder.decode(frame)


