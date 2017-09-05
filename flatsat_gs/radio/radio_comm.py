import imp
import os
import sys
import re
import aprs
import kiss

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
    parser.add_argument('-t', '--target_gr', required=True,
                        help="GNURadio host", default='localhost')                 
    parser.add_argument('-p', '--port_gr', required=True,
                        help="GNURadio port", default=52001, type=int)
    parser.add_argument('-u', '--target_dw', required=True,
                        help="DireWolf host", default='localhost')                 
    parser.add_argument('-v', '--port_dw', required=True,
                        help="DireWolf port", default=8001, type=int)

    args = parser.parse_args()
    imp.load_source('config', args.config)

    class MyPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [(Token.Prompt, 'COMM'),
                    (Token.Prompt, '> ')]

    cfg = Config()
    frame_decoder = response_frames.FrameDecoder(response_frames.frame_factories)


    def receive():
        rcv = Receiver(args.target_gr, args.port_gr)
        rcv.connect()
        data = rcv.decode_kiss(rcv.receive())        
        rcv.disconnect()
        return frame_decoder.decode(data)

    def send(frame):
        sender = Sender(args.target_dw, args.port_dw)
        sender.connect()
        sender.send(frame)        
        sender.disconnect()

    def send_receive(frame):
        send(frame)
        return receive()

    def get_file(file_dict):
        sender = Sender(args.target_dw, args.port_dw)
        sender.connect()
        receiver = Receiver(args.target_gr, args.port_gr)
        receiver.connect()
        downloader = RemoteFile(sender, receiver)
        data = downloader.download(file_dict)
        sender.disconnect()
        receiver.disconnect()

        return data


    shell = InteractiveShellEmbed(config=cfg, user_ns={'receive': receive, 'send' : send, 'send_receive' : send_receive, 'parse_file_list' : RemoteFileTools.parse_file_list, 'get_file' : get_file, 'RemoteFileTools' : RemoteFileTools, 'RemoteFile' : RemoteFile},
                                  banner2='COMM Terminal')
    shell.prompts = MyPrompt(shell)
    shell.run_code('from telecommand import *')
    shell()
