import sys
import os
import thread
import time
from Queue import Queue, Empty
from enum import Enum

sys.path.append('..')
sys.path.append('../integration_tests')

from radio.sender import Sender
from radio.receiver import Receiver

from devices.comm import BeaconFrame
from response_frames.period_message import PeriodicMessageFrame


class Tmtc:
    def __init__(self, timeout=70):
        self.sender = Sender()
        self.receiver = Receiver()

        self.rx_queue = Queue()
        self.last_beacon = None
        self.correlation_id = 0

        thread.start_new_thread(self._receive_thread, ())
        self.wait_for_first_beacon(timeout)

    def wait_for_first_beacon(self, timeout):
        end_time = time.time() + timeout
        while self.beacon() == None:
            if end_time < time.time():
                raise self.TimeoutException()

    def _receive_thread(self):
        while True:
            try:
                frame = self.receiver.receive_frame()
                if isinstance(frame, BeaconFrame):
                    self.last_beacon = frame
                elif isinstance(frame, PeriodicMessageFrame):
                    # periodic - nothing for now
                    pass
                else:
                    # definitely requested by operator
                    self.rx_queue.put(frame)
            except IndexError:
                pass

    def get(self, timeout=None):
        # .get() cannot be killed by Ctrl+C - workaround
        if timeout is not None:
            return self.rx_queue.get(timeout=timeout)
        else:
            # infinite timeout, but can be killed
            try:
                return self.rx_queue.get(timeout=100)
            except Empty:
                pass

    def flush(self):
        try:
            self.rx_queue.get(block=False)
        except Empty:
            return

    def beacon(self):
        return self.last_beacon

    def beacon_value(self, element):
        from tools.parse_beacon import ParseBeacon
        return ParseBeacon.parse(self.beacon())\
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

    def get_correct_frame(self, id, response_type):
        response = self.rx_queue.get(timeout=5)
        if isinstance(response, response_type):
            if id == response.correlation_id:
                print "OK %d" % id
                return response
            else:
                print "Correlation id mismatch %d != %d" % (response.correlation_id, id)
                raise self.CorrelationMismatchException()
        else:
            print "Incorrect response type: ", response
            raise TypeError()

    def send_tc_with_response(self, type, response_type, *args):
        id = self.get_correlation_id()
        frame = type(id, *args)

        for _ in xrange(3):
            try:
                self.send_raw(frame)
                f = self.get_correct_frame(id, response_type)
                return f
            except TypeError:
                print "Wrong type Exception"
                self.flush()
                print "Repeat! %d" % _
            except self.CorrelationMismatchException:
                print "Bad correlation ID Exception"
                self.flush()
                print "Repeat! %d" % _
            except Empty:
                print "Empty queue Exception"
                print "Repeat! %d" % _
        raise self.FrameGetFail()

    def send_tc_with_multi_response(self, type, response_type, *args):
        id = self.get_correlation_id()
        frame = type(id, *args)

        self.send_raw(frame)

        responses = []
        while True:
            try:
                response = self.get_correct_frame(id, response_type)
                responses.append(response)
            except Empty:
                print "Timeout!"
                return responses

    def send(self, tc):
        return tc.send(self)



    # def file_list(self, path):
    #     frames = self.send_tc_with_multi_response(tc.fs.ListFiles, response_frames.file_system.FileListSuccessFrame, path)
    #     from tools.remote_files import RemoteFileTools
    #
    #     files = []
    #     for f in frames:
    #         files.extend(RemoteFileTools.parse_file_list(f))
    #     return files
    #
    # def file_remove(self, path):
    #     response = self.send_tc_with_response(tc.fs.RemoveFile, response_frames.common.FileRemoveSuccessFrame, path)
    #     file_removed = ''.join(map(chr, response.payload()[2:]))
    #     if file_removed != path:
    #         raise Exception("Incorrect path returned" + file_removed)
    #     print "File %s removed!" % file_removed
    #
    # def disable_overheat_submode(self, side):
    #     mapping = {"A": 0, "B": 1}
    #     return self.send_tc_with_response(tc.eps.DisableOverheatSubmode, response_frames.disable_overheat_submode.DisableOverheatSubmodeSuccessFrame, mapping[side])
    #
    # def abort_experiment(self):
    #     return self.send_tc_with_response(tc.experiments.AbortExperiment,
    #                                       response_frames.common.ExperimentSuccessFrame)



if __name__ == "__main__":
    from IPython.terminal.embed import InteractiveShellEmbed
    from IPython.terminal.prompts import Prompts
    from pygments.token import Token

    class MyPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [(Token.Prompt, 'TMTC'),
                    (Token.Prompt, '> ')]

    tmtc = Tmtc()

    shell = InteractiveShellEmbed(user_ns={'tmtc': tmtc},
                                  banner2='TMTC Terminal')
    shell.prompts = MyPrompt(shell)
    shell.run_code('import tc')
    shell.run_code('import time')
    shell()


