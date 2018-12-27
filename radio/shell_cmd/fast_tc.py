import telecommand as tc
from radio.task_actions import WaitMode


def build(sender, rcv, frame_decoder, analyzer, ns):
    def files():
        if files.cid == 255:
            files.cid = 200

        ns['run']([
            [tc.ListFiles(files.cid, '/'), ns['Send'], WaitMode.Wait]
        ])

        files.cid += 1

    files.cid = 200

    return {
        'files': files
    }
