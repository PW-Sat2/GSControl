import struct
from collections import defaultdict

from typing import List

import response_frames
from summary.scope import session
from utils import ensure_string


def save_memory_files():
    memory_frames = only_type(session.all_frames, response_frames.MemoryContent) # type: List[response_frames.MemoryContent]

    packs = defaultdict(list)

    for frame in memory_frames:
        packs[frame.correlation_id].append(frame)

    for cid in packs.keys():
        chunks = sorted(packs[cid], key=lambda f: f.seq())
        chunks = unique_seqs(chunks)

        with session.open_artifact('memory_content_{}'.format(cid), 'wb') as f:
            for c in chunks:
                f.write(ensure_string(c.content))


def unpack_binary_file(file_name, fmt, from_byte=0):
    raw = session.read_artifact(file_name, binary=True)
    raw = raw[from_byte:]
    size = struct.calcsize(fmt)
    part = ensure_string(raw[0:size])

    return struct.unpack(fmt, part)