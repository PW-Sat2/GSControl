import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *
from parameters import *


class SetAdcsModeParameters(Parameters):
    MODE_OFFSET = 1
    END_OF_PARAMS_OFFSET = 2
    PATH_INCLUDED = False

    ADCS_MODE_BUILT_IN_DETUMBLING = 0
    
    def __init__(self, frame_payload):
        self.mode = self.get_parameters(frame_payload)[self.MODE_OFFSET]


class SetAdcsMode:
    def __init__(self, frame_payload):
        self.parameters = SetAdcsModeParameters(frame_payload)

    def task_duration(self):
        duration = 0
        if self.is_adcs_power_on(self.parameters):
            duration = 23 * 60 * 60
        return Duration(duration)
    
    def mean_powers(self):
        if self.is_adcs_power_on(self.parameters):
            mean_power = (Adcs.MEAN_POWER_CONSUMPTION * 1000.0) / Eps.EFFICIENCY_5V0
            return MeanPowers([mean_power, mean_power, mean_power, mean_power])
        return MeanPowers([0, 0, 0, 0])

    @classmethod
    def is_adcs_power_on(self, parameters):
        if parameters.mode >= parameters.ADCS_MODE_BUILT_IN_DETUMBLING:
            return True
        return False
