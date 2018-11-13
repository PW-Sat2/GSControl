def build_shell_commands(sender, rcv, frame_decoder, analyzer, user_ns):
    r = {}

    from .base_io import build as build_base_io
    from .tasklist import build as build_tasklist
    from .parsing import build as build_parsing
    from .utils import build as build_utils

    r.update(build_base_io(sender, rcv, frame_decoder, analyzer, user_ns))
    r.update(build_tasklist(sender, rcv, frame_decoder, analyzer, user_ns))
    r.update(build_parsing(sender, rcv, frame_decoder, analyzer, user_ns))
    r.update(build_utils(sender, rcv, frame_decoder, analyzer, user_ns))

    return r

__all__ = ['build_shell_commands']
