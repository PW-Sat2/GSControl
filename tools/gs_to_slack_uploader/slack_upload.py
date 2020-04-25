from threading import Thread, Event
import sys
import os
import logging
import requests
import time
import datetime
from pprint import pformat

sys.path.append(os.path.join(os.path.dirname(
    __file__), '../../build/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(
    __file__), '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from radio.radio_frame_decoder import *
from remote_files import RemoteFileTools
from utils import ensure_string, ensure_byte_list

decoder = response_frames.FrameDecoder(response_frames.frame_factories)


class UploadSlack(Thread):
    def __init__(self, frames_queue, slack_url, gs_name):
        Thread.__init__(self)
        self.frames_queue = frames_queue
        self._stop_event = Event()
        self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.slack_url = slack_url

        self.gs_emoji = self._gs_emoji(gs_name) 

    def _gs_emoji(self, gs_name):
        switcher = {
            "elka"  : ":elka:",
            "fp-gs" : ":kp:"
        }
        return switcher.get(gs_name, ":question:")

    def put_slack(self, frame):
        try:
            packet = self.rcv.get_packet()
            return packet
        except:
            return None

    def stop(self):
        self._stop_event.set()

    def run(self):
        self.logger.log(logging.INFO, "Starting Slack Uploader thread.")
        while not self._stop_event.is_set():
            try:
                packet = self.frames_queue.popleft()
                date_earth = datetime.datetime.fromtimestamp(packet['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                decoded_frame = packet['frame']
                date_mission = ""

                frame_text = pformat(decoded_frame)

                frame_text_new = ""
                formated_message = ""

                if isinstance(decoded_frame, response_frames.BeaconFrame):
                    date_mission += str(decoded_frame._parsed['03: Time Telemetry']['0072: Mission time'])[:-7]
                    formated_message = "{0}  *{1}* | :pwsat2: *{2}*\r\n{3}\r\n".format(self.gs_emoji, date_earth, date_mission, self._format_message_new(frame_text))
                elif isinstance(decoded_frame, response_frames.file_system.FileListSuccessFrame):
                    frame_text = self._format_file_list(decoded_frame)
                    formated_message = "{0}  *{1}*\r\n{2}\r\n".format(self.gs_emoji, date_earth, frame_text)
                else:
                    formated_message = "{0}  *{1}*:   {2}\r\n".format(self.gs_emoji, date_earth, frame_text)

                # filter out FileSendSuccessFrame
                if isinstance(decoded_frame, response_frames.common.FileSendSuccessFrame):
                    self.logger.log(logging.DEBUG, frame_text)
                elif isinstance(decoded_frame, response_frames.common.FileSendErrorFrame):
                    self.logger.log(logging.DEBUG, frame_text)
                else:
                    requests.post(self.slack_url, json={'username': 'GS Frames', 'text': formated_message})

            except IndexError:
                time.sleep(0.1)

        self.logger.log(logging.INFO, "Finished Slack Uploader thread.")


    def _format_message_new(self, frame_text):
        frame_text_split = frame_text.split("\n")
        frame_formated_message = ""

        # format first line
        if frame_text_split[0] == "BeaconFrame @ 9600 bps":
            frame_formated_message += "         " + frame_text_split[0] + "\r\n"
        else:
            frame_formated_message += ":x: " + frame_text_split[0] + "\r\n"

        # check other lines for correctness
        for i in frame_text_split[1:-1]:
            # filter out some lines
            if i.find("GYRO UNCAL") != -1 or \
               i.find("EXPERIMENT") != -1 or \
               i.find("OBC CRC") != -1:
                continue

            # find warnings
            if i.find("!!!!!") != -1:
                frame_formated_message += ":x: " + i[5:] + "\r\n"
            else:
                frame_formated_message += "        " + i[5:] + "\r\n"

        return frame_formated_message


    def _format_file_list(self, frame):
        file_list = RemoteFileTools.parse_file_list(frame)
        files = pformat(frame) + "\r\n"
        for f in file_list:
            files += ">{0}:    {1}\r\n".format(f['File'], f['Chunks'])
        return files


