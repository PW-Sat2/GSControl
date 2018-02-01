import imp
import os
import sys

import zmq
from zmq.utils.win32 import allow_interrupt

try:
    from utils import ensure_string, ensure_byte_list
    import response_frames
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils import ensure_string, ensure_byte_list
    import response_frames
    from radio_frame_decoder import FallbackResponseDecorator


class Receiver:
    def __init__(self, target="localhost", port=7001):
        self.context = zmq.Context.instance()
        self.sock = self.context.socket(zmq.SUB)
        self.sock.connect("tcp://%s:%d" % (target, port))
        self.sock.setsockopt(zmq.SUBSCRIBE, "")
        self.timeout(-1)
        self.abort_send = self.context.socket(zmq.PAIR)
        self.abort_recv = self.context.socket(zmq.PAIR)

        self.abort_send.bind('inproc://receiver/abort')
        self.abort_recv.connect('inproc://receiver/abort')

    def connect(self):
        print "Connect not used. Remove!"
        pass

    def timeout(self, timeout_in_ms=-1):
        self.set_timeout = timeout_in_ms
        self.sock.setsockopt(zmq.RCVTIMEO, self.set_timeout)

    def receive(self):
        while self.receive_no_wait() is not None:
            pass

        def stop():
            self.abort_send.send('QUIT')

        self._flush_socket(self.abort_recv, -1)

        with allow_interrupt(stop):
            (read, _, _) = zmq.select([self.sock, self.abort_recv], [], [self.sock, self.abort_recv])

            if read[0] == self.sock:
                return self.sock.recv()
            elif read[0] == self.abort_recv:
                return None
            else:
                return None

    def receive_no_wait(self):
        self.sock.setsockopt(zmq.RCVTIMEO, 0)
        val = None
        try:
            val = self.sock.recv()
        except zmq.Again:
            pass
        finally:
            self.sock.setsockopt(zmq.RCVTIMEO, self.set_timeout)
            return val

    def decode_kiss(self, frame):
        frame = frame[16:]

        return ensure_byte_list(frame)

    def make_frame(self, frame):
        frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))
        return frame_decoder.decode(frame)

    def receive_frame(self):
        rcv = self.receive()
        rcv = self.decode_kiss(rcv)
        rcv = self.make_frame(rcv)
        return rcv

    def disconnect(self):
        print "Disconnect not used. Remove!"

    def _flush_socket(self, socket, timeout):
        socket.setsockopt(zmq.RCVTIMEO, 0)

        while True:
            try:
                socket.recv()
            except zmq.Again:
                break

        socket.setsockopt(zmq.RCVTIMEO, timeout)


if __name__ == '__main__':
    try:
        from obc import OBC, SerialPortTerminal
    except ImportError:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from obc import OBC, SerialPortTerminal

    import argparse
    from IPython.terminal.embed import InteractiveShellEmbed
    from IPython.terminal.prompts import Prompts
    from pygments.token import Token
    from traitlets.config.loader import Config
    from utils import ensure_byte_list
    import response_frames

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', required=True,
                        help="Config file (in CMake-generated integration tests format, only MOCK_COM required)")
    parser.add_argument('-t', '--target', required=True,
                        help="GNURadio host", default='localhost')
    parser.add_argument('-p', '--port', required=True,
                        help="GNURadio port", default=52001, type=int)

    args = parser.parse_args()
    imp.load_source('config', args.config)

    class MyPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [(Token.Prompt, 'COMM'),
                    (Token.Prompt, '> ')]

    cfg = Config()
    frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))

    def receive():
        rcv = Receiver(args.target, args.port)
        rcv.connect()
        data = rcv.decode_kiss(rcv.receive())
        rcv.disconnect()
        return frame_decoder.decode(data)

    shell = InteractiveShellEmbed(config=cfg, user_ns={'receive': receive},
                                  banner2='COMM Terminal')
    shell.prompts = MyPrompt(shell)
    shell.run_code('from telecommand import *')
    shell()
