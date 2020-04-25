import Queue
from receive_distribute import ReceiveDistribute
from slack_upload import UploadSlack
from log import setup_log
import time
import logging
from collections import deque
import signal
import argparse
import sys


def signal_handler(sig, frame):
        logger.log(logging.INFO, "Finishing")
        rcv_dist.stop()
        rcv_dist.join()
        upload.stop()
        upload.join()
        sys.exit(0)


parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', required=True,
                help="Slack URL to upload")
parser.add_argument('-g', '--gs', required=True,
                help="GS Name")
parser.add_argument('-v', '--verbose', action='store_true',
                help="Verbose / debug mode")

args = parser.parse_args()
slack_url = args.url
gs_name = args.gs

setup_log(args.verbose)
logger = logging.getLogger()

frames_queue = deque()
rcv_dist = ReceiveDistribute(frames_queue)
upload = UploadSlack(frames_queue, slack_url, gs_name)
logger.log(logging.INFO, "Starting Slack Uploader services")
rcv_dist.start()
upload.start()

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to finish...')

while True:
    time.sleep(10)    
