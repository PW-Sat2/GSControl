import argparse
import logging
from datetime import datetime
from threading import Thread
from urlparse import urlparse

import zmq
from influxdb import InfluxDBClient

import response_frames
from data_point import generate_data_points
from devices import BeaconFrame
from radio.radio_receiver import Receiver
from tools.parse_beacon import ParseBeacon


class BeaconUploaderApp(object):
    @staticmethod
    def main(args):
        parser = argparse.ArgumentParser()

        parser.add_argument('-t', '--downlink-host', required=False,
                            help="GNURadio host", default='localhost')
        parser.add_argument('-p', '--downlink-port', required=False,
                            help="GNURadio port", default=7001, type=int)

        parser.add_argument('-d', '--influx', required=False,
                            help="InfluxDB url", default='http://localhost:8086/pwsat2')

        parser.add_argument('-g', '--gs', required=True,
                            help="Ground Station tag")

        BeaconUploaderApp(parser.parse_args(args))._run()

    def __init__(self, args):
        self._args = args
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

        self._new_frame_push.bind("inproc://grafana_uploader/new_msg")
        self._new_frame_pull.connect("inproc://grafana_uploader/new_msg")

        self._abort_pub.bind("inproc://grafana_uploader/abort")
        self._publisher_abort.connect("inproc://grafana_uploader/abort")

    def _abort(self):
        self._log.info('Terminating...')
        self._abort_pub.send('ABORT')

    def _run(self):
        self._receiver_thread.start()
        self._publisher_thread.start()

        try:
            while True:
                input()
        except KeyboardInterrupt:
            self._abort()

    def _receiver_worker(self):
        self._receiver_log.info("Waiting for beacons from tcp://%s:%d", self._args.downlink_host, self._args.downlink_port)

        while True:
            frame = self._receiver.receive_no_wait()
            if frame:
                self._receiver_log.info("Got frame without wait")
            else:
                self._receiver_log.info("Waiting for frame")
                frame = self._receiver.receive()

            if not frame:
                self._receiver_log.error('Nothing received')
                continue

            self._receiver_log.info('Pushing frame for processing')
            self._new_frame_push.send_pyobj((datetime.utcnow(), frame))

    def _publisher_worker(self):
        self._publisher_log.info('Waiting for frames and publishing to %s', self._args.influx)
        while True:
            (r, _, _) = zmq.select([self._new_frame_pull, self._publisher_abort], [], [self._new_frame_pull, self._publisher_abort])

            if r[0] == self._publisher_abort:
                self._publisher_log.info('Terminating')
                break
            else:
                self._new_frame_pull.recv_pyobj()

            (ts, frame) = self._new_frame_pull.recv_pyobj()

            data = self._receiver.decode_kiss(frame)
            try:
                self._process_single_frame(ts, data)
            except Exception as e:
                self._publisher_log.error('Error processing received frame: %s', str(e))

        self._publisher_log.info('Finished')

    def _process_single_frame(self, ts, raw_frame):
        frame = self._frame_decoder.decode(raw_frame)

        if not isinstance(frame, BeaconFrame):
            return

        self._publisher_log.info("Received beacon frame")
        self._process_single_beacon(ts, frame)

    def _process_single_beacon(self, timestamp, beacon):
        telemetry = ParseBeacon.parse(beacon)

        points = generate_data_points(timestamp, telemetry, {
            'ground_station': self._args.gs
        })

        url = urlparse(self._args.influx)
        db = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

        db.write_points(points)
        db.close()
