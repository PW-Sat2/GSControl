import base64
from os import path
from utils import ensure_byte_list
from radio.radio_frame_decoder import FallbackResponseDecorator
import response_frames


class SessionView(object):
    def __init__(self, store, session_number):
        self._store = store
        self._session_number = session_number
        self._root = path.join(store.root, 'sessions', str(session_number))

        self._frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))

    def _expand_path(self, relative_path):
        return path.join(self._root, relative_path)

    def get_file(self, file_path, binary=False, as_lines=False):
        full_path = self._expand_path(file_path)
        mode = 'r'
        if binary:
            mode += 'b'

        with open(full_path, mode) as f:
            if as_lines:
                return f.readlines()

            data = f.read()
            if binary:
                data = ensure_byte_list(data)

        return data

    def write_artifact(self, file_path, content, binary=False):
        full_path = self._expand_path(path.join('artifacts', file_path))
        mode = 'w'
        if binary:
            mode += 'b'

        with open(full_path, mode) as f:
            f.write(content)

    def frames(self, sources, unique_only=True):
        payloads = []

        for source in sources:
            frames_file = self.get_file('artifacts/{}_downlink.frames'.format(source), as_lines=True)
            for line in frames_file:
                (ts, direction, payload) = parts = line.split(',')

                if direction != 'D':
                    continue

                payloads.append(payload)

        if unique_only:
            payloads = list(set(payloads))

        frames = []

        for payload in payloads:
            binary_frame = base64.b64decode(payload)
            binary_frame = binary_frame[16:-2]
            binary_frame = ensure_byte_list(binary_frame)
            frame = self._frame_decoder.decode(binary_frame)

            frames.append(frame)

        return list(frames)


class MissionStore(object):
    def __init__(self, root):
        self.root = root

    def get_session(self, session_number):
        return SessionView(self, session_number)
