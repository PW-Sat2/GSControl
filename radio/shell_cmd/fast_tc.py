import telecommand as tc
from radio.task_actions import WaitMode
from devices.comm import BaudRate
import sys


def build(sender, rcv, frame_decoder, analyzer, ns):
    def files():
        if files.cid == 255:
            files.cid = 200

        ns['run']([
            [tc.ListFiles(files.cid, '/'), ns['Send'], WaitMode.Wait]
        ])

        files.cid += 1

    files.cid = 200
    
    def bitrate_1200():
        if bitrate_1200.cid == 200:
            bitrate_1200.cid = 175
        
        ns['run']([
            [tc.SetBitrate(bitrate_1200.cid, BaudRate.BaudRate1200), ns['Send'], WaitMode.Wait]
        ])
        
        bitrate_1200.cid += 1
    
    bitrate_1200.cid = 175

    def bitrate_9600():
        if bitrate_9600.cid == 175:
            bitrate_9600.cid = 150

        ns['run']([
            [tc.SetBitrate(bitrate_9600.cid, BaudRate.BaudRate9600), ns['Send'], WaitMode.Wait]
        ])

        bitrate_9600.cid += 1

    bitrate_9600.cid = 150

    def sail():
        print('Are you sure to perform Sail Experiment? Type SAIL (uppercase) to confirm: ')
        user = sys.stdin.readline()

        if user.replace('\n', '').replace('\r', '') == 'SAIL':
            if sail.cid == 125:
                sail.cid = 100

            ns['run']([
                [tc.PerformSailExperiment(sail.cid), ns['Send'], WaitMode.Wait]
            ])

            sail.cid += 1
        else:
            print("Wrong answer. No Sail Experiment performed.")

    sail.cid = 100

    def down_sail(*chunks):
        chunks = list(chunks)
        if not chunks:
            print 'Nothing to download'
            return

        ns['run']([
            [tc.DownloadFile(correlation_id=13, path='/sail.exp', seqs=chunks), ns['Send'], WaitMode.Wait]
        ])

    def down_photo(photo_id, *chunks):
        chunks = list(chunks)
        if not chunks:
            chunks = range(0, 25, 1)

        photo_file = '/sail.photo_{}'.format(photo_id)

        ns['run']([
            [tc.DownloadFile(correlation_id=13, path=photo_file, seqs=chunks), ns['Send'], WaitMode.Wait]
        ])

    return {
        'files': files,
        'bitrate_1200': bitrate_1200,
        'bitrate_9600': bitrate_9600,
        'sail': sail,
        'down_sail': down_sail,
        'down_photo': down_photo
    }
