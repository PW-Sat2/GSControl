import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *


class SadsExperiment:
    def task_duration(self):
        return Duration(Sads.EXPERIMENT_DURATION)

    @classmethod
    def experiment_energy_consumption(self):
        return Energy(Sads.EXPERIMENT_ENERGY_CONSUMPTION)

    @classmethod
    def data_frames_count(self):
        return 21

    @classmethod
    def photo_frames_count(self):
        return Camera.PHOTO_480_MAX_FULL_FRAMES

    @classmethod
    def total_frames_count(self):
        return self.photo_frames_count() + self.data_frames_count()

    def downlink_frames_count(self):
        return self.total_frames_count()

    def downlink_durations(self):
        return Comm.downlink_durations(self.total_frames_count())

    @classmethod
    def downlink_energy_consumption(self, bitrate):
        transmission_time = Comm.downlink_frames_duration(self.total_frames_count(), bitrate)
        return Comm.downlink_energy_consumption(transmission_time)

    def energy_consumptions(self):
        energy_1200 = float(self.experiment_energy_consumption() + self.downlink_energy_consumption(1200))
        energy_2400 = float(self.experiment_energy_consumption() + self.downlink_energy_consumption(2400))
        energy_4800 = float(self.experiment_energy_consumption() + self.downlink_energy_consumption(4800))
        energy_9600 = float(self.experiment_energy_consumption() + self.downlink_energy_consumption(9600))
        return Energys([energy_1200, energy_2400, energy_4800, energy_9600])

    def storage_usage(self):
        return Storage((self.downlink_frames_count() * Comm.FULL_FRAME) / 1024.0)
