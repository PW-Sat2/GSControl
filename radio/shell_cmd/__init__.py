def build_shell_commands(sender, rcv, frame_decoder, analyzer, user_ns, monitor_connector):
    r = {}

    from .base_io import build as build_base_io
    from .tasklist import build as build_tasklist
    from .parsing import build as build_parsing
    from .utils import build as build_utils
    from .fast_tc import build as build_fast_tc

    r.update(build_base_io(sender, rcv, frame_decoder, analyzer, user_ns))
    r.update(build_tasklist(sender, rcv, frame_decoder, analyzer, user_ns, monitor_connector))
    r.update(build_parsing(sender, rcv, frame_decoder, analyzer, user_ns))
    r.update(build_utils(sender, rcv, frame_decoder, analyzer, user_ns))
    r.update(build_fast_tc(sender, rcv, frame_decoder, analyzer, user_ns))

    return r

__all__ = ['build_shell_commands']
