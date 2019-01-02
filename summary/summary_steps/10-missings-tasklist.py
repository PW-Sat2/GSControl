# import logging
# from collections import defaultdict
# from pprint import pformat, pprint

# import response_frames
# from tools.remote_files import RemoteFileTools
from summary.scope import session

from tools.generate_tasklist import MissingFilesTasklistGenerator

def generate_missings_tasklist():
    telecommandsText = MissingFilesTasklistGenerator.generate(session, 20, 30)
    session.write_artifact('tasklist.missing.py', telecommandsText)