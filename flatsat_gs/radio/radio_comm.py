import imp
import os
import sys
import re
import aprs
import kiss
import time

if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from radio_receiver import *
    from radio_sender import *
    from tools.remote_files import *
    import response_frames

    from obc import OBC, SerialPortTerminal

    import argparse
    from IPython.terminal.embed import InteractiveShellEmbed
    from IPython.terminal.prompts import Prompts
    from pygments.token import Token
    from traitlets.config.loader import Config
    import socket
    from utils import ensure_string, ensure_byte_list
    

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', required=True,
                        help="Config file (in CMake-generated integration tests format, only MOCK_COM required)")
    parser.add_argument('-t', '--downlink-host', required=False,
                        help="GNURadio host", default='localhost')                 
    parser.add_argument('-p', '--downlink-port', required=False,
                        help="GNURadio port", default=7001, type=int)
    parser.add_argument('-u', '--uplink-host', required=False,
                        help="Uplink host", default='*')
    parser.add_argument('-v', '--uplink-port', required=False,
                        help="Uplink port", default=7000, type=int)

    args = parser.parse_args()
    imp.load_source('config', args.config)

    class MyPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [(Token.Prompt, 'COMM'),
                    (Token.Prompt, '> ')]

    cfg = Config()
    frame_decoder = response_frames.FrameDecoder(response_frames.frame_factories)
    
    sender = Sender(args.uplink_host, args.uplink_port)
    rcv = Receiver(args.downlink_host, args.downlink_port)

    def receive():
        data = rcv.decode_kiss(rcv.receive())        
        return frame_decoder.decode(data)

    def receive_raw():
        return rcv.decode_kiss(rcv.receive())
    
    def set_timeout(timeout_in_ms=-1):
        rcv.timeout(timeout_in_ms)

    def send(frame):
        sender.send(frame)

    def send_receive(frame):
        send(frame)
        return receive()

    def get_sender():
        return sender

    def get_receiver():
        return rcv

    def get_beacon():
        from tools.parse_beacon import ParseBeacon
        return ParseBeacon.parse(send_receive(SendBeacon()))

    def get_file(file_dict):
        downloader = RemoteFile(sender, rcv)
        data = downloader.download(file_dict)

        return data


    shell = InteractiveShellEmbed(config=cfg, user_ns={'receive_raw' : receive_raw, 'receive': receive, 'set_timeout': set_timeout, 'send' : send, 'send_receive' : send_receive, 'parse_file_list' : RemoteFileTools.parse_file_list, 'get_file' : get_file, 'RemoteFileTools' : RemoteFileTools, 'RemoteFile' : RemoteFile, 'sender': sender, 'receiver': rcv, 'get_beacon': get_beacon},
                                  banner2='COMM Terminal')
    shell.prompts = MyPrompt(shell)
    shell.run_code('from tools.parse_beacon import ParseBeacon')
    shell.run_code('import telecommand as tc')
    shell.run_code('import time')
    shell()
