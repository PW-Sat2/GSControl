import thread
import time
from Queue import Queue, Empty

from radio.sender import Sender
from radio.receiver import Receiver

from devices.comm import BeaconFrame
from response_frames.period_message import PeriodicMessageFrame
from tools.log import PrintLog, MainLog, SimpleLogger

from tools.parse_beacon import ParseBeacon
from pprint import pformat


class Tmtc:
    def __init__(self, timeout=70):
        self.sender = Sender()
        self.receiver = Receiver()

        self.rx_queue = Queue()
        self.last_beacon = None
        self.parsed_beacon = {}
        self.beacon_logger = SimpleLogger('beacon.log', in_test=True)

        self.correlation_id = 0

        thread.start_new_thread(self._receive_thread, ())
        self.first_beacon_timeout = timeout

    def wait_for_first_beacon(self, timeout):
        MainLog("Waiting for first beacon...")
        end_time = time.time() + timeout
        while self.last_beacon is None:
            from tc.comm import SendBeacon
            self.send(SendBeacon())
            time.sleep(5)
            if end_time < time.time():
                raise self.TimeoutException()
        MainLog("First beacon received")

    def _receive_thread(self):
        while True:
            try:
                frame = self.receiver.receive_frame()
                if isinstance(frame, BeaconFrame):
                    self.update_beacon(frame)
                elif isinstance(frame, PeriodicMessageFrame):
                    # periodic - nothing for now
                    pass
                else:
                    # definitely requested by operator
                    self.rx_queue.put(frame)
            except IndexError:
                pass

    def flush(self):
        try:
            self.rx_queue.get(block=False)
        except Empty:
            return

    def update_beacon(self, frame):
        self.last_beacon = frame

        self.parsed_beacon = ParseBeacon.parse(self.beacon())
        self.beacon_logger.log(pformat(self.parsed_beacon))

    def beacon(self):
        if self.last_beacon is None:
            self.wait_for_first_beacon(self.first_beacon_timeout)
        return self.last_beacon

    def beacon_value(self, element):

        return self.parsed_beacon\
            .get(element[0])\
            .get(element[1]).converted

    def send_raw(self, tc):
        self.sender.send(tc)

    def get_correlation_id(self):
        tmp = self.correlation_id
        self.correlation_id += 1
        if self.correlation_id == 256:
            self.correlation_id = 0
        return tmp

    class CorrelationMismatchException(BaseException):
        pass

    class FrameGetFail(BaseException):
        pass

    class TimeoutException(BaseException):
        pass

    def get_correct_frame(self, correlation_id, response_type, timeout=5):
        response = self.rx_queue.get(timeout=timeout)
        if isinstance(response, response_type):
            if correlation_id == response.correlation_id:
                return response
            else:
                PrintLog("Correlation id mismatch {} != {}".format(response.correlation_id, correlation_id))
                raise self.CorrelationMismatchException()
        else:
            PrintLog("Incorrect response type: {}".format(response))
            raise TypeError()

    def send_tc_with_response(self, tc_type, response_type, *args, **kwargs):
        correlation_id = self.get_correlation_id()
        frame = tc_type(correlation_id, *args)
        timeout = kwargs.pop('timeout', 5)

        for _ in xrange(3):
            try:
                self.send_raw(frame)
                f = self.get_correct_frame(correlation_id, response_type, timeout)
                PrintLog("TC[{}] {}".format(correlation_id, tc_type.__name__))
                return f
            except TypeError:
                PrintLog("Wrong type Exception")
                self.flush()
            except self.CorrelationMismatchException:
                PrintLog("Bad correlation ID Exception")
                self.flush()
            except Empty:
                PrintLog("No response from S/C!")
            PrintLog("Repeat! {}".format(_))
        raise self.FrameGetFail()

    def send_tc_with_multi_response(self, tc_type, response_type, *args, **kwargs):
        correlation_id = self.get_correlation_id()
        frame = tc_type(correlation_id, *args)
        timeout = kwargs.pop('timeout', 5)

        self.send_raw(frame)

        responses = []
        PrintLog("TC[{}] {}".format(correlation_id, tc_type.__name__))
        while True:
            try:
                response = self.get_correct_frame(correlation_id, response_type, timeout)
                responses.append(response)
                PrintLog("TC[{}]-response{}: {}".format(correlation_id, len(responses), tc_type.__name__))
            except Empty:
                PrintLog("TC[{}] Timeout, got {} response frames".format(correlation_id, len(responses)))
                return responses

    def send(self, tc):
        return tc.send(self)
