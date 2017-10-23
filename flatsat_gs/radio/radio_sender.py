import imp
import os
import sys
import re
import aprs
import kiss
import time
import zmq
import pmt
import array

try:
    from utils import ensure_string, ensure_byte_list
    import response_frames
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    from utils import ensure_string, ensure_byte_list
    import response_frames


class Sender:
    def __init__(self, target="*", port=7000, source_callsign='SP3SAT', destination_callsign='PWSAT2-0'):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.PUB)
        #self.sock.bind("tcp://%s:%d" % (target, port))
        self.sock.connect("tcp://localhost:7000")
        time.sleep(1)
        
        self.aprs_frame = aprs.Frame()
        self.aprs_frame.source = aprs.Callsign(source_callsign)
        self.aprs_frame.destination = aprs.Callsign(destination_callsign)

    def connect(self):
        pass

    def send(self, frame):
        payload = frame.build()
        self.aprs_frame.text = ensure_string(payload)
        buff = array.array('B', self.aprs_frame.encode_kiss())
        msg = pmt.serialize_str(pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(buff), buff)))
        self.sock.send(msg)
        
    def disconnect(self):
        pass


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
    parser.add_argument('-t', '--target', required=False,
                        help="Target", default='*')                 
    parser.add_argument('-p', '--port', required=False,
                        help="Port", default=7000, type=int)

    args = parser.parse_args()
    imp.load_source('config', args.config)

    class MyPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [(Token.Prompt, 'SENDER'),
                    (Token.Prompt, '> ')]

    cfg = Config()
    sender = Sender(args.target, args.port)
    sender.connect()

    shell = InteractiveShellEmbed(config=cfg, user_ns={'send': sender.send},
                                  banner2='COMM Sender Terminal')
    shell.prompts = MyPrompt(shell)
    shell.run_code('from telecommand import *')
    shell()
