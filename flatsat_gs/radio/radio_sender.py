import imp
import os
import sys
import re
import aprs
import kiss
from udpkiss import UDPKISS

try:
    from utils import ensure_string, ensure_byte_list
    import response_frames
    from uplink_test import UDPKISS
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../GS-Modem/uplink'))
    from utils import ensure_string, ensure_byte_list
    import response_frames
    from uplink_test import UDPKISS


class Sender:
    def __init__(self, target, port, source_callsign='SP3SAT', destination_callsign='PWSAT2-0'):
        self.target = target
        self.port = port
        self.aprs_frame = aprs.Frame()
        self.aprs_frame.source = aprs.Callsign(source_callsign)
        self.aprs_frame.destination = aprs.Callsign(destination_callsign)

    def connect(self):
        self.ki = UDPKISS(host=self.target, port=self.port)
        self.ki.start()

    def send(self, frame):
        payload = frame.build()
        self.aprs_frame.text = ensure_string(payload)
        self.ki.write(self.aprs_frame.encode_kiss())

    def disconnect(self):
        self.ki.stop()


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
                        help="DireWolf host", default='localhost')                 
    parser.add_argument('-p', '--port', required=True,
                        help="DireWolf port", default=52001, type=int)

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
