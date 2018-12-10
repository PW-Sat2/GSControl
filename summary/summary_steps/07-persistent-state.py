import logging
from pprint import pformat

import response_frames
from persistent_state import PersistentStateParser
from summary.scope import session
from utils import ensure_string


def save_persistent_state():
    state_frames = only_type(session.all_frames, response_frames.PersistentStateFrame)

    if len(state_frames) == 0:
        return

    state_frames = sorted(state_frames, key=lambda f: f.seq())

    content = []
    for f in state_frames:
        content += f.payload()

    content = ensure_string(content)

    logging.info("Saving perisistent state ({} chunks, {} bytes)".format(len(state_frames), len(content)))

    session.write_artifact('persistent_state.raw', binary=True, content=content)

    parsed = PersistentStateParser.parse_partial(content)

    text = pformat(parsed[0])

    session.write_artifact('persistent_state.txt', content=text)
