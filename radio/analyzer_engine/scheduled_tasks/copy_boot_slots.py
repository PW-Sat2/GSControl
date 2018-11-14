import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *

class PerformCopyBootSlots:
    def task_duration(self):
        return Duration(10 * 60)

    def energy_consumptions(self):
        energy = ((self.task_duration().__float__() * Obc.FLASH_POWER_CONSUMPTION) / 3600.0) * 1000.0
        return Energys([energy, energy, energy, energy])
