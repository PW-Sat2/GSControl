import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *
from parameters import *

class SetPeriodicMessageParameters(Parameters):
    INTERVAL_MINUTES_OFFSET = 1
    REPEAT_COUNT_OFFSET = 2
    END_OF_PARAMS_OFFSET = 3

    def __init__(self, frame_payload):
        self.interval_minutes = self.get_parameters(frame_payload)[self.INTERVAL_MINUTES_OFFSET]
        self.repeat_count = self.get_parameters(frame_payload)[self.REPEAT_COUNT_OFFSET]
        self.message = self.get_parameters(frame_payload)[self.END_OF_PARAMS_OFFSET]

class SetPeriodicMessage:
    def __init__(self, frame_payload):
        self.parameters = SetPeriodicMessageParameters(frame_payload)

    def task_duration(self):
        return Duration(Duration.PERSISTENT)

    def mean_powers(self):
        mean_1200 = self.periodic_mean_power(self.parameters, 1200)
        mean_2400 = self.periodic_mean_power(self.parameters, 2400)
        mean_4800 = self.periodic_mean_power(self.parameters, 4800)
        mean_9600 = self.periodic_mean_power(self.parameters, 9600)
        return MeanPowers([mean_1200, mean_2400, mean_4800, mean_9600])

    @classmethod
    def downlink_frames_count(self):
        return 1

    @classmethod
    def periodic_mean_power(self, parameters, bitrate):
        preamble = float(Comm.DOWNLINK_MAX_PREAMBLE)
        if bitrate == 9600:
            preamble = float(Comm.DOWNLINK_MAX_PREAMBLE_9600)
        tx_time = (((Comm.FULL_FRAME * 8.0) / bitrate) + preamble) * parameters.repeat_count
        return ((tx_time / (parameters.interval_minutes * 60.0)) * Comm.DOWNLINK_POWER_CONSUMPTION) * 1000.0

