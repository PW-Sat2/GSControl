import sys
import os

try:
    from utils import ensure_string, ensure_byte_list
    import response_frames
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils import ensure_string, ensure_byte_list
    import response_frames


class InvalidFrame:
    def __init__(self, raw, error):
        self._raw = raw
        self._error = error


class FallbackResponseDecorator:
    def __init__(self, frame_decoder):
        self._frame_decoder = frame_decoder

    def decode(self, frame):
        try:
            return self._frame_decoder.decode(frame)
        except Exception as e:
            return InvalidFrame(frame, e)
