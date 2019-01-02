import pprint
import threading
from datetime import datetime
import zmq
from utils import ensure_byte_list

from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.styles import style_from_dict
from pygments.token import Token
import response_frames as rf

from radio.radio_receiver import Receiver

Decoder = rf.FrameDecoder(rf.frame_factories)

STYLE = style_from_dict({
    Token.Timestamp: '#fdf6e3',
    Token.CurrentStep: '#b58900',
    Token.TotalSteps: '#6c71c4',
    Token.Action: '#dc322f',
    Token.Telecommand: '#268bd2',
})


class SessionScope(object):
    def __init__(self, sender):
        self.sender = sender

    def send(self, frame):
        self.sender.send(frame)


def build_recv_sock(target, port):
    context = zmq.Context.instance()
    sock = context.socket(zmq.SUB)
    sock.connect("tcp://%s:%d" % (target, port))
    sock.setsockopt(zmq.SUBSCRIBE, "")

    return sock

def receive_all(receivers, callback):
    signal = threading.Event()
    signal.clear()

    started = threading.Event()

    def worker():
        socks = map(lambda s: s, receivers)

        started.set()

        while True:
            (r, _, _) = zmq.select(socks, [], [], timeout=2)

            if not r and signal.is_set():
                break
                pass

            for socket in r:
                frame_raw = socket.recv()
                frame_raw = frame_raw[16:-2]
                frame_raw = ensure_byte_list(frame_raw)
                frame = Decoder.decode(frame_raw)
                callback(frame)

    t = threading.Thread(target=worker)
    t.start()
    started.wait()

    def end():
        signal.set()
        t.join()

    return end


class Loop(object):
    def __init__(self, tasks, until=None):
        self.until = until
        self.tasks = tasks

    def _execute_once(self, session_scope):
        for step_no, step in enumerate(self.tasks):
            [telecommand, action_type] = step

            tokens = [
                (Token.String, "["),
                (Token.Timestamp, datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')),
                (Token.String, "] "),
                (Token.String, "Step "),
                (Token.CurrentStep, str(step_no + 1)),
                (Token.String, "/"),
                (Token.TotalSteps, str(len(self.tasks))),
                (Token.String, ": "),
                (Token.Action, action_type.__name__),
                (Token.String, "("),
                (Token.Telecommand, pprint.pformat(telecommand)),
                (Token.String, ")...\n")
            ]

            print_tokens(tokens, style=STYLE)

            action_type(telecommand).do(session_scope)

    def _eval_until(self, received_frames):
        if self.until is None:
            return True

        return self.until(received_frames)

    def __call__(self, session_scope):
        received_frames = []

        while True:
            end_receive = receive_all([
                build_recv_sock(target='fp-main.gs.kplabs.pl', port=7001),
                build_recv_sock(target='elka-main.gs.pw-sat.pl', port=7001),
            ], callback=lambda f: received_frames.append(f))

            self._execute_once(session_scope)

            end_receive()

            if self._eval_until(received_frames):
                break
