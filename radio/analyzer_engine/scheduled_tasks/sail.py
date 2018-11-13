import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *


class SailExperiment:
    @classmethod
    def task_duration(self):
        return Duration(Sail.SAIL_EXP_DURATION)

    @classmethod
    def downlink_frames_count(self):
        return self.photo_frames_count() + self.data_frames_count()

    @classmethod
    def storage_usage(self):
        return Storage((self.downlink_frames_count() * Comm.FULL_FRAME) / 1024.0)

    @classmethod
    def data_frames_count(self):
        return 22

    @classmethod
    def photo_frames_count(self):
        SMALL_PHOTO_QTY = 64
        FINAL_PHOTO_QTY = 2
        return Camera.PHOTO_128_MAX_FULL_FRAMES * SMALL_PHOTO_QTY + FINAL_PHOTO_QTY * Camera.PHOTO_480_MAX_FULL_FRAMES

    @classmethod
    def downlink_frames_count(self):
        return self.data_frames_count() + self.photo_frames_count()

    @classmethod
    def experiment_energy_consumption(self):
        themal_knives_energy = 120 * 2 * Sail.SAIL_TK_POWER / 3600.0
        pld_board_energy = Sail.SAIL_EXP_DURATION * (Sail.PLD_SENS_AVERAGE_POWER_5V0 + Sail.SUNS_REF_AVERAGE_POWER_5V0) / Eps.EFFICIENCY_5V0 / 3600.0
        cameras_energy = Sail.SAIL_EXP_DURATION * 2 * Camera.CAMERA_POWER / Eps.EFFICIENCY_3V3 / 3600.0

        return Energy((themal_knives_energy + pld_board_energy + cameras_energy) * 1000.0)

    @classmethod
    def downlink_energy_consumption(self, bitrate):
        transmission_time = Comm.downlink_frames_duration(self.downlink_frames_count(), bitrate)
        return Comm.downlink_energy_consumption(transmission_time)

    @classmethod
    def energy_consumptions(self):
        energy_1200 = float(self.experiment_energy_consumption() + self.downlink_energy_consumption(1200))
        energy_2400 = float(self.experiment_energy_consumption() + self.downlink_energy_consumption(2400))
        energy_4800 = float(self.experiment_energy_consumption() + self.downlink_energy_consumption(4800))
        energy_9600 = float(self.experiment_energy_consumption() + self.downlink_energy_consumption(9600))
        return Energys([energy_1200, energy_2400, energy_4800, energy_9600])

    @classmethod
    def downlink_durations(self):
        return Comm.downlink_durations(self.downlink_frames_count())
