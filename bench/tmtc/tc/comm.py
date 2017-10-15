import telecommand.comm as comm
from response_frames.common import CommSuccessFrame
from response_frames.set_bitrate import SetBitrateSuccessFrame


class EnterIdleState(object):
    def __init__(self, time_in_seconds):
        self.time_in_seconds = time_in_seconds

    def send(self, tmtc):
        tmtc.send_tc_with_response(comm.EnterIdleState, CommSuccessFrame, self.time_in_seconds)


class SetBitrate(object):
    def __init__(self, bitrate_in_bps):
        mapping = {1200: 1, 2400: 2, 4800: 4, 9600: 8}
        self.value = mapping[bitrate_in_bps]

    def send(self, tmtc):
        return tmtc.send_tc_with_response(comm.SetBitrate, SetBitrateSuccessFrame, self.value)


class SendBeacon(object):
    def send(self, tmtc):
        return tmtc.send_raw(comm.SendBeacon())