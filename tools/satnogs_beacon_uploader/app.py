import argparse
import logging
from datetime import datetime
from threading import Thread
from urlparse import urlparse
from urllib import urlencode
import urllib2
import imp
import os

import zmq

import response_frames
from devices import BeaconFrame
from response_frames.deep_sleep_beacon import DeepSleepBeacon
from response_frames.little_oryx import LittleOryxDeepSleepBeacon
from radio.radio_receiver import Receiver


class SatnogsUploaderApp(object):
    @staticmethod
    def parse_args(args):
        parser = argparse.ArgumentParser()

        parser.add_argument('-t', '--downlink-host', required=False,
                            help="GNURadio host", default='localhost')
        parser.add_argument('-p', '--downlink-port', required=False,
                            help="GNURadio port", default=7001, type=int)

        parser.add_argument('-c', '--config', required=True,
                        help="Config with Satnogs data",
                        default=os.path.join(os.path.dirname(__file__), 'satnogs_config.py'))
      
        parser.add_argument('-s', '--silent', action='store_true',
                            help="Suppress most of output (service use)")

        parser.add_argument('-u', '--upload', action='store_true',
                            help="Do actual upload.")

        return parser.parse_args(args)

    @staticmethod
    def main(args):
        args_parsed = SatnogsUploaderApp.parse_args(args)
        config = SatnogsUploaderApp._validate_config(args_parsed)
        if config is not None:
            SatnogsUploaderApp(args_parsed, config)._run()
        
    @staticmethod
    def main_with_args_parsed(args_parsed):
        config = SatnogsUploaderApp._validate_config(args_parsed)
        if config is not None:        
            SatnogsUploaderApp(args_parsed, config)._run()

    @staticmethod
    def _validate_config(args):
        imp.load_source('config', args.config)
        from config import config

        if not config.viewkeys() >= {'NORAD_ID', 'SATNOGS_URL', 'GS_CALLSIGN', 'GS_LATITUDE', 'GS_LONGITUDE'}:
            print("Required data not provided in config. Exiting.")
            return -1
        else:
            print("Config OK!")
            print("NORAD_ID: {}".format(config['NORAD_ID']))
            print("SATNOGS_URL: {}".format(config['SATNOGS_URL']))
            print("GS_CALLSIGN: {}".format(config['GS_CALLSIGN']))
            print("GS_LATITUDE: {} deg".format(config['GS_LATITUDE']))
            print("GS_LONGITUDE: {} deg".format(config['GS_LONGITUDE']))

        return config

    def __init__(self, args, config):
        self._args = args
        self._config = config
        self._log = logging.getLogger("App")
        self._receiver_log = logging.getLogger("Receiver")
        self._publisher_log = logging.getLogger("Publisher")

        self._receiver = Receiver(args.downlink_host, args.downlink_port, on_stop=self._abort)
        self._frame_decoder = response_frames.FrameDecoder(response_frames.frame_factories)

        self._receiver_thread = Thread(target=self._receiver_worker)
        self._receiver_thread.setDaemon(True)

        self._publisher_thread = Thread(target=self._publisher_worker)
        self._receiver_thread.setDaemon(True)

        self._abort_pub = zmq.Context.instance().socket(zmq.PAIR)
        self._publisher_abort = zmq.Context.instance().socket(zmq.PAIR)

        self._new_frame_push = zmq.Context.instance().socket(zmq.PUSH)
        self._new_frame_pull = zmq.Context.instance().socket(zmq.PULL)

        self._new_frame_push.bind("inproc://satnogs_uploader/new_msg")
        self._new_frame_pull.connect("inproc://satnogs_uploader/new_msg")

        self._abort_pub.bind("inproc://satnogs_uploader/abort")
        self._publisher_abort.connect("inproc://satnogs_uploader/abort")

    def _abort(self):
        self._log.info('Terminating...')
        self._abort_pub.send('ABORT')

    def _run(self):
        self._log.info('SatNOGS uploader starting...')
        self._receiver_thread.start()
        self._publisher_thread.start()

        try:
            while True:
                input()
        except KeyboardInterrupt:
            self._abort()

    def _receiver_worker(self):
        self._receiver_log.info("Waiting for beacons from tcp://%s:%d", self._args.downlink_host, self._args.downlink_port)

        i = 0

        while True:
            frame = self._receiver.receive_no_wait()
            if frame:
                self._receiver_log.debug("Got frame without wait")
            else:
                self._receiver_log.debug("Waiting for frame")
                frame = self._receiver.receive()

            if not frame:
                self._receiver_log.error('Nothing received')
                continue

            self._receiver_log.debug('Pushing frame {} for processing'.format(i))
            self._new_frame_push.send_pyobj((datetime.utcnow(), i, frame))
            i += 1

    def _publisher_worker(self):
        self._publisher_log.info('Waiting for frames and publishing to %s', self._config['SATNOGS_URL'])
        while True:
            (r, _, _) = zmq.select([self._new_frame_pull, self._publisher_abort], [], [self._new_frame_pull, self._publisher_abort])

            if r[0] == self._publisher_abort:
                self._publisher_log.debug('Terminating')
                break

            (ts, i, frame) = self._new_frame_pull.recv_pyobj()
            self._receiver_log.debug('Recevied frame {}'.format(i))

            data = self._receiver.decode_kiss(frame)
            try:
                self._process_single_frame(ts, data, frame)
            except Exception as e:
                self._publisher_log.error('Error processing received frame: %s', str(e))

        self._publisher_log.info('Finished')

    def _process_single_frame(self, ts, raw_frame, raw_full_ax25_frame):
        frame = self._frame_decoder.decode(raw_frame)

        if isinstance(frame, BeaconFrame):
            self._publisher_log.debug("Received beacon frame")
            self._upload_frame(ts, raw_full_ax25_frame)
        elif isinstance(frame, DeepSleepBeacon):
            self._publisher_log.debug("Received deep sleep beacon frame")
            self._upload_frame(ts, raw_full_ax25_frame)
        elif isinstance(frame, LittleOryxDeepSleepBeacon):
            self._publisher_log.debug("Received Little Oryx beacon frame")
            self._upload_frame(ts, raw_full_ax25_frame)
        else:
            self._publisher_log.debug("Not a beacon")
            return

        self._publisher_log.debug("Published")

    def _upload_frame(self, timestamp, raw_full_ax25_frame):
        frame = raw_full_ax25_frame[:-2]
        self._submit(frame, timestamp)

    def _prepare_request(self):
        longitude = self._config['GS_LONGITUDE']
        latitude = self._config['GS_LATITUDE']
        request = { 'noradID': str(self._config['NORAD_ID']),
                    'source': self._config['GS_CALLSIGN'],
                    'locator': 'longLat',
                    'longitude': str(abs(longitude)) + ('E' if longitude >= 0 else 'W'),
                    'latitude': str(abs(latitude)) + ('N' if latitude >= 0 else 'S'),
                    'version': '1.6.6' 
                }

        return request

    def _submit(self, frame, timestamp):
        url = self._config['SATNOGS_URL']
        request = self._prepare_request()
           
        request['frame'] = frame.encode('hex').upper()
        request['timestamp'] = timestamp.isoformat()[:-3] + 'Z'

        params = urlencode(request) 

        if not self._args.upload:
            print(params)
            return
        
        try:
            response = urllib2.urlopen(url, data=params)
        except Exception as e:
            self._publisher_log.exception('Error while submitting telemetry', exc_info=e)
            return
        reply = response.read()
        code = response.getcode()
        if code < 200 or code >= 300:
            self._publisher_log.error("Server error while submitting telemetry")
            self._publisher_log.error("Reply:")
            self._publisher_log.error(reply)
            self._publisher_log.error("URL: %s", response.geturl())
            self._publisher_log.error("HTTP code: %s", response.getcode())
            self._publisher_log.error("Info:")
            self._publisher_log.error(response.info())
        response.close()
