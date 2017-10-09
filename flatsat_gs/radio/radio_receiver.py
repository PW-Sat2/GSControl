import imp
import os
import sys
import re
import socket
import time
import zmq
import pmt
import array

try:
    from utils import ensure_string, ensure_byte_list
    import response_frames
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils import ensure_string, ensure_byte_list
    import response_frames


class Receiver:
    def __init__(self, target="localhost", port=7001):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.SUB)
        self.sock.connect("tcp://%s:%d" %(target, port))
        self.sock.setsockopt(zmq.SUBSCRIBE, "")
        self.timeout(-1)

    def connect(self):
        print "Connect not used. Remove!"
        pass

    def timeout(self, timeout_in_ms=-1):
        self.set_timeout = timeout_in_ms
        self.sock.setsockopt(zmq.RCVTIMEO, self.set_timeout)

    def receive(self):
        while self.receive_no_wait() is not None:
            pass
        x = pmt.u8vector_elements(pmt.cdr(pmt.deserialize_str(self.sock.recv())))
        val = ''.join(map(chr, x))
        return val

    def receive_no_wait(self):
        self.sock.setsockopt(zmq.RCVTIMEO, 0)
        val = None
        try:
            val = pmt.u8vector_elements(pmt.cdr(pmt.deserialize_str(self.sock.recv())))
        except zmq.Again:
            pass
        finally:
            self.sock.setsockopt(zmq.RCVTIMEO, self.set_timeout)
            return val
            
    def decode_kiss(self, frame):
        frame = frame[16:-2]
        
        return ensure_byte_list(frame)


    def make_frame(self, frame):
        frame_decoder = response_frames.FrameDecoder(response_frames.frame_factories)
        return frame_decoder.decode(frame)

    def receive_frame(self):
        rcv = self.receive()
        rcv = self.decode_kiss(rcv)
        rcv = self.make_frame(rcv)
        return rcv


    def disconnect(self):
        print "Disconnect not used. Remove!"


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
    import socket
    from utils import ensure_string, ensure_byte_list
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
    frame_decoder = response_frames.FrameDecoder(response_frames.frame_factories)


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
