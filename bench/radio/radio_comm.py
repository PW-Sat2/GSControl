import imp
import os
import sys
import zmq


if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from receiver import Receiver
    from sender import Sender
    from tools.remote_files import *

    from IPython.terminal.embed import InteractiveShellEmbed
    from IPython.terminal.prompts import Prompts
    from pygments.token import Token

    class MyPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [(Token.Prompt, 'COMM'),
                    (Token.Prompt, '> ')]

    sender = Sender()
    rcv = Receiver()
    time.sleep(0.1)

    def receive():
        return rcv.receive_frame()

    def receive_raw():
        return rcv.receive_raw()

    def set_timeout(timeout_in_ms=-1):
        rcv.set_timeout(timeout_in_ms)

    def send(frame):
        sender.send(frame)

    def send_receive(frame):
        send(frame)
        return receive()

    def get_sender():
        return sender

    def get_receiver():
        return rcv

    def clear():
        set_timeout(0)
        while True:
            try:
                receive_raw()
            except zmq.Again:
                return
            finally:
                set_timeout(-1)

    def get_beacon():
        from tools.parse_beacon import ParseBeacon
        return ParseBeacon.parse(send_receive(SendBeacon()))

    def get_file(file_dict):
        downloader = RemoteFile(sender, rcv)
        data = downloader.download(file_dict)

        return data


    shell = InteractiveShellEmbed(user_ns={'receive_raw' : receive_raw, 'receive': receive, 'set_timeout': set_timeout, 'send' : send, 'send_receive' : send_receive, 'parse_file_list' : RemoteFileTools.parse_file_list, 'get_file' : get_file, 'RemoteFileTools' : RemoteFileTools, 'RemoteFile' : RemoteFile, 'sender': sender, 'receiver': rcv, 'get_beacon': get_beacon},
                                  banner2='COMM Terminal')
    shell.prompts = MyPrompt(shell)
    shell.run_code('from tools.parse_beacon import ParseBeacon')
    shell.run_code('import telecommand as tc')
    shell.run_code('import time')
    shell()
