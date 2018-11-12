import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *
from parameters import *

class IdleStateParameters(Parameters):
    DURATION_OFFSET = 1
    END_OF_PARAMS_OFFSET = 2
    PATH_INCLUDED = False

    def __init__(self, frame_payload):
        self.duration = self.get_parameters(frame_payload)[self.DURATION_OFFSET]


class IdleState:
    def __init__(self, frame_payload):
        self.parameters = IdleStateParameters(frame_payload)

    def task_duration(self):
        return Duration(self.parameters.duration)

    def energy_consumptions(self):
        energy = ((self.parameters.duration / 3600.0) * Comm.DOWNLINK_POWER_CONSUMPTION) * 1000.0
        return Energys([energy, energy, energy, energy])
