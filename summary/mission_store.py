import base64
from os import path
import os
import json
import dateutil.parser

from radio import analyzer
from utils import ensure_byte_list, ensure_string
from radio.radio_frame_decoder import FallbackResponseDecorator
import response_frames


class SessionView(object):
    def __init__(self, store, session_number):
        self._store = store
        self.session_number = session_number
        self._root = path.join(store.root, 'sessions', str(session_number))

        self._frame_decoder = FallbackResponseDecorator(
            response_frames.FrameDecoder(response_frames.frame_factories))

        self.tasklist_path = self.expand_path('tasklist.py')

        self.tasklist = []
        if path.exists(self.tasklist_path):
            self.tasklist = store.load_tasklist(self.tasklist_path)

        if self.has_artifact('all.frames'):
            self.all_frames = self.frames(['all'])

    def read_metadata(self):
        metadata = json.loads(self.get_file('data.json'))["Session"]
        metadata["start_time_iso_with_zone"] = dateutil.parser.parse(
            metadata["start_time_iso_with_zone"])
        metadata["stop_time_iso_with_zone"] = dateutil.parser.parse(
            metadata["stop_time_iso_with_zone"])

        return metadata

    def expand_path(self, relative_path):
        return path.join(self._root, relative_path)

    def expand_artifact_path(self, relative_path):
        return self.expand_path(path.join('artifacts', relative_path))

    def get_file(self, file_path, binary=False, as_lines=False):
        full_path = self.expand_path(file_path)
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

    def read_artifact(self, file_path, binary=False, as_lines=False):
        return self.get_file(path.join('artifacts', file_path), binary=binary, as_lines=as_lines)

    def open_artifact(self, file_path, mode):
        full_path = self.expand_path(path.join('artifacts', file_path))

        directory = path.dirname(full_path)

        if not path.isdir(directory):
            os.mkdir(directory)

        return open(full_path, mode)

    def write_artifact(self, file_path, content, binary=False):
        mode = 'w'
        if binary:
            mode += 'b'

        with self.open_artifact(file_path, mode) as f:
            f.write(content)

    def frames(self, sources, unique_only=True):
        def sorter(x):
            try:
                return (x.correlation_id, x.ReceivedAPID, x._seq)
            except:
                return (0,0,0)

        payloads = []

        for source in sources:
            file_name = 'artifacts/{}_downlink.frames'.format(source)
            if source == 'all':
                file_name = 'artifacts/all.frames'

            frames_file = self.get_file(file_name, as_lines=True)
            for line in frames_file:
                (ts, direction, payload) = line.split(',')

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

        result = list(frames)
        result.sort(key= sorter)
        return result

    def has_artifact(self, file_name):
        full_path = self.expand_artifact_path(file_name)
        # print(full_path)

        return path.exists(full_path)

    def remove_artifact(self, file_name):
        if self.has_artifact(file_name):
            full_path = self.expand_artifact_path(file_name)
            os.remove(full_path)


class MissionStore(object):
    def __init__(self, root):
        self.root = root
        self.analyzer = analyzer.Analyzer()
        self._sessions = {}

    def get_session(self, session_number):
        if not session_number in self._sessions:
            self._sessions[session_number] = SessionView(self, session_number)

        return self._sessions[session_number]

    def load_tasklist(self, file_path):
        return self.analyzer.load(file_path)
