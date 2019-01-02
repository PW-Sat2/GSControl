def only_type(frames, frame_type):
    return filter(lambda f: isinstance(f, frame_type), frames)


def unique_seqs(frames):
    result = []
    seqs = set()

    for frame in frames:
        if frame.seq() in seqs:
            continue

        result.append(frame)
        seqs.add(frame.seq())

    return result
