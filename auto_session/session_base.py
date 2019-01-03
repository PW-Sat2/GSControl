import pprint
import threading
from datetime import datetime

import zmq

import response_frames as rf
from utils import ensure_byte_list

Decoder = rf.FrameDecoder(rf.frame_factories)


class SessionScope(object):
    def __init__(self, sender, receivers):
        self.receivers = receivers
        self.sender = sender

    def send(self, frame):
        self.sender.send(frame)


def receive_all(receivers, callback):
    signal = threading.Event()
    signal.clear()

    started = threading.Event()

    def worker():
        started.set()

        while True:
            (r, _, _) = zmq.select(receivers, [], [], timeout=2)

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
    def __init__(self, title, tasks, until=None):
        self.title = title
        self.until = until
        self.tasks = tasks

    def _execute_once(self, session_scope):
        for step_no, step in enumerate(self.tasks):
            [telecommand, action_type] = step

            print '\t{:%H:%M:%S:%f}: Step {}/{}\t{}({})'.format(
                datetime.now(),
                step_no + 1,
                len(self.tasks),
                action_type.__name__,
                pprint.pformat(telecommand)
            )

            action_type(telecommand).do(session_scope)

    def _eval_until(self, received_frames):
        if self.until is None:
            return True

        return self.until(received_frames)

    def __call__(self, session_scope):
        received_frames = []
        counter = 1

        def on_frame(f):
            received_frames.append(f)
            print '\tFrame: {}'.format(repr(f))

        while True:
            print '{} Iteration: {}'.format(self.title, counter)
            end_receive = receive_all(session_scope.receivers, callback=on_frame)

            self._execute_once(session_scope)

            end_receive()

            if self._eval_until(received_frames):
                break

            counter += 1
