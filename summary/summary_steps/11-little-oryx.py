import os
import logging

from summary.scope import session, lo_tools_path
import subprocess


def parse_little_oryx_logs(memory_content_cids):
    paths = [session.expand_artifact_path('memory_content_' + str(cid)) for cid in memory_content_cids]
    paths = [f for f in paths if os.path.exists(f)]
    exts = ['', '.cmd', '.sh']
    tool_path = None
    for e in exts:
        try_tool_path = os.path.join(lo_tools_path, 'decode_little_oryx_logs' + e)
        if os.path.exists(try_tool_path):
            tool_path = try_tool_path
            break

    if tool_path is None:
        logging.warn('Skipping Little Oryx logs decode as decoder was not found (tools path: {})'.format(lo_tools_path))
        return

    process = subprocess.Popen([
        tool_path,
    ] + paths, stdout=subprocess.PIPE, shell=True, universal_newlines=True)

    (decoded_logs, _) = process.communicate()

    session.write_artifact('logs.txt', decoded_logs)
