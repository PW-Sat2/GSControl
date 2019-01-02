from summary.scope import session

from tools.generate_tasklist import MissingFilesTasklistGenerator

def generate_missings_tasklist():
    telecommandsText = MissingFilesTasklistGenerator.generate(session, max_chunks=20, cid_start=30)
    session.write_artifact('tasklist.missing.py', telecommandsText)