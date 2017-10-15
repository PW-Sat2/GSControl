import zmq
import pmt
import array

from utils import ensure_string


class Sender:
    def __init__(self):
        from config import config
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.PUB)
        self.sock.connect("tcp://%s:7000" % config['GS_HOST'])

        self.source = config['SOURCE_CALLSIGN']
        self.destination = config['DESTINATION_CALLSIGN']

    @staticmethod
    def encode_callsign(call):
        return ''.join([chr(ord(i) << 1) for i in call])

    def header(self):
        return ''.join([
            self.encode_callsign(self.destination),
            chr(96),
            self.encode_callsign(self.source),
            chr(97),
            chr(3),
            chr(0xF0)
        ])

    def build(self, text):
        return ''.join([
            self.header(),
            text
        ])

    def send(self, frame):
        payload = frame.build()
        frame = self.build(ensure_string(payload))
        buff = array.array('B', frame)
        msg = pmt.serialize_str(pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(buff), buff)))
        self.sock.send(msg)
