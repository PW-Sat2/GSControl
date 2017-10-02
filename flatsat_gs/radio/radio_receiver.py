import imp
import os
import sys
import re
import socket

try:
    from utils import ensure_string, ensure_byte_list
    import response_frames
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils import ensure_string, ensure_byte_list
    import response_frames


class Receiver:
    def __init__(self, target, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (target, port)

    def connect(self):
        self.sock.bind(self.server_address)

    def timeout(self, timeout):
        self.sock.settimeout(timeout)

    def receive(self):
        buff = ""

        while True:
            data = self.sock.recv(1024)
            buff += data
            if data.find('\xC0') is not -1:
                break
   
        return buff

    def receive_no_wait(self):
        try:
            buff = ""

            while True:
                data = self.sock.recv(1024)
                buff += data
                if data.find('\xC0') is not -1:
                    break
       
            return buff
        except:
            return None


    def decode_kiss(self, frame):
        frame = frame[18:-1]
        frame = frame.replace('\xDB\xDC', '\xC0')
        frame = frame.replace('\xDB\xDD', '\xDB')
        
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
        # self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


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
