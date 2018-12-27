import os
import sys

from datetime import datetime

if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from radio_receiver import *
    from radio_sender import *
    from tools.remote_files import *
    from analyzer import *
    import response_frames
    from devices.adcs import *

    import argparse
    from IPython.terminal.embed import InteractiveShellEmbed
    from IPython.terminal.prompts import Prompts
    from pygments.token import Token
    from traitlets.config.loader import Config
    from utils import ensure_string, ensure_byte_list
    from radio_frame_decoder import FallbackResponseDecorator

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', required=False,
                        help="Config file (in CMake-generated integration tests format)",
                        default=os.path.join(os.path.dirname(__file__), 'config.py'))
    parser.add_argument('-t', '--downlink-host', required=False,
                        help="GNURadio host", default='localhost')
    parser.add_argument('-p', '--downlink-port', required=False,
                        help="GNURadio port", default=7001, type=int)
    parser.add_argument('-u', '--uplink-host', required=False,
                        help="Uplink host", default='localhost')
    parser.add_argument('-v', '--uplink-port', required=False,
                        help="Uplink port", default=7000, type=int)
    parser.add_argument('-s', '--session', required=False,
                        help="Current session to fetch tasklist", default=0, type=int)
    parser.add_argument('-r', '--receiver', help="Start receiver loop", action='store_true')

    args = parser.parse_args()
    imp.load_source('config', args.config)
    from config import config

    prompt = 'COMM'
    banner = 'COMM Terminal'
    try:
        uplink_callsign_test = aprs.Callsign(config['COMM_UPLINK_CALLSIGN'])
    except:
        prompt = 'NO_UPLINK'
        banner = 'COMM Terminal WITHOUT UPLINK'


    class MyPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [(Token.Prompt, prompt),
                    (Token.Prompt, '> ')]

    cfg = Config()
    frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))

    sender = Sender(args.uplink_host, args.uplink_port, source_callsign=config['COMM_UPLINK_CALLSIGN'])
    rcv = Receiver(args.downlink_host, args.downlink_port)
    analyzer = Analyzer()


    def static_var(varname, value):
        def decorate(func):
            setattr(func, varname, value)
            return func
        return decorate
    
    def get_file(file_dict):
        downloader = RemoteFile(sender, rcv)
        data = downloader.download(file_dict)

        return data

    def jebnij_bekona():
        import telecommand
        sender.send(telecommand.SendBeacon())

    @static_var("cid", 200)
    def files():
        import telecommand
        if files.cid == 255:
            files.cid = 200

        sender.send(telecommand.ListFiles(files.cid, '/'))
        print("File list requested, cid={0}".format(files.cid))
        files.cid += 1
    
    user_ns = {                                 
            'get_file': get_file, 
            'RemoteFileTools': RemoteFileTools,
            'RemoteFile': RemoteFile, 
            'sender': sender,
            'receiver': rcv,
            'jebnij_bekona': jebnij_bekona,
            'files': files
    }

    from shell_cmd import build_shell_commands

    shell_cmds = build_shell_commands(sender, rcv, frame_decoder, analyzer, user_ns)

    user_ns.update(shell_cmds)

    shell = InteractiveShellEmbed(config=cfg, user_ns=user_ns,
                                  banner2=banner)
    shell.prompts = MyPrompt(shell)
    shell.run_code('from tools.parse_beacon import ParseBeacon')
    shell.run_code('import telecommand as tc')
    shell.run_code('import time')
    shell.run_code('from pprint import pprint')
    shell.run_code('import datetime')
    shell.run_code('from devices import camera')
    shell.run_code('from tools.remote_files import *')
    shell.run_code('from radio.task_actions import *')
    shell.run_code('import response_frames')
    shell.run_code('import response_frames as rf')

    if args.session != 0:
        tasklist_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mission', 'sessions', str(args.session), 'tasklist.py')
        shell.run_code('tasks = load(\"{}\")'.format(tasklist_file))
        shell.run_code('analyze(tasks)')
        shell.set_next_input('run(tasks)')

    if args.receiver:
        shell.run_code('frames = receiver_loop()')
        shell.set_next_input('frames = receiver_loop()')

    shell()
