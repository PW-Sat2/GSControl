import time
import argparse

import zmq
import pmt
import socket

class CommMockToZmq(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.context = zmq.Context()
        self.socket_uplink = self.context.socket(zmq.SUB)
        self.socket_downlink = self.context.socket(zmq.PUB)

        self.socket_uplink.bind("tcp://*:%s" % 7000)
        self.socket_downlink.bind("tcp://*:%s" % 7001)

        self.socket_uplink.setsockopt(zmq.SUBSCRIBE, '')

    def get(self, nr):
        so_far = ''
        while len(so_far) < nr:
            now = self.socket_mock.recv(nr-len(so_far))
            so_far += now
        return so_far
    
    def mock_uplink(self, packet):
        self.socket_mock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_mock.connect((self.host, self.port))

        print "Uplink: ", map(ord, packet)

        frame = 'S' + chr(len(packet)) + packet
        self.socket_mock.sendall(frame)
        assert (self.get(3) == 'ACK')

        self.socket_mock.close()


    @staticmethod
    def encode_callsign(call):
        return ''.join([chr(ord(i) << 1) for i in call])

    @staticmethod
    def build_kiss_header():
        return ''.join([
            CommMockToZmq.encode_callsign('PWSAT2'),
            chr(96),
            CommMockToZmq.encode_callsign('PWSAT2'),
            chr(97),
            chr(3),
            chr(0xF0)
        ])

    @staticmethod
    def build_kiss(text):
        return ''.join([
            CommMockToZmq.build_kiss_header(),
            text,
            '\x00\x00'
        ])

    def mock_downlink(self):
        self.socket_mock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_mock.connect((self.host, self.port))

        self.socket_mock.sendall('R')
        assert(self.get(3) == 'ACK')
        frames_nr = ord(self.get(1))

        frames = []
        for _ in xrange(frames_nr):
            length = ord(self.get(1))
            data = self.get(length)
            frames.append(data)
            print "Downlink: ", map(ord, data)

        assert (self.get(3) == 'ACK')

        self.socket_mock.close()

        return frames

    def loop(self):
        while True:
            time.sleep(0.1)
            try:
                while True:
                    pmt_frame = self.socket_uplink.recv(flags=zmq.NOBLOCK)
                    frame = pmt.u8vector_elements(pmt.cdr(pmt.deserialize_str(pmt_frame)))
                    just_content = frame[16:]
                    self.mock_uplink(''.join(map(chr, just_content)))
            except zmq.ZMQError:
                pass

            try:
                downlink_frames = self.mock_downlink()
                for i in downlink_frames:
                    table = map(ord, self.build_kiss(i))
                    msg = pmt.serialize_str(pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(table), table)))
                    self.socket_downlink.send(msg)
            except socket.error:
                print("Exception in socket!")
                




parser = argparse.ArgumentParser()

parser.add_argument('-t', '--target', required=True,
                    help="Host with Just-Mocks", default='localhost')
parser.add_argument('-p', '--port', required=True,
                    help="Just-Mocks port", default=1234, type=int)

args = parser.parse_args()

x = CommMockToZmq(args.target, args.port)
x.loop()
