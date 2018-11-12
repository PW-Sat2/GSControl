import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *

class PayloadCommissioning:
    '''
    Resources utilization for Payload Commissioning.

    Source: PWSat2-SVN/system/tests_and_reports/29 -
            Experiments power consumption estimation/data/plots
    '''

    @classmethod
    def task_duration(self):
        return Duration(300)

    @classmethod
    def storage_usage(self):
        return self.data_file_storage_usage() + self.photo_storage_usage()

    @classmethod
    def data_file_frames_count(self):
        return 8

    @classmethod
    def data_file_storage_usage(self):
        return Storage((self.data_file_frames_count() * Comm.FULL_FRAME) / 1024)

    @classmethod
    def photo_frames_count(self):
        return 2 * (Camera.PHOTO_128_MAX_FULL_FRAMES + Camera.PHOTO_240_MAX_FULL_FRAMES + Camera.PHOTO_480_MAX_FULL_FRAMES)

    @classmethod
    def photo_storage_usage(self):
        return Storage((self.photo_frames_count() * Comm.FULL_FRAME) / 1024)

    @classmethod
    def payload_energy_consumption(self):
        energy_3V3_wh = Pld.PLD_3V3_ENERGY_CONSUMPTION / Eps.EFFICIENCY_3V3
        energy_5v_wh = Pld.SENS_5V0_ENERGY_CONSUMPTION / Eps.EFFICIENCY_5V0

        return Energy((energy_5v_wh + energy_3V3_wh) * 1000.0)

    @classmethod
    def downlink_energy_consumption(self, bitrate):
        transmission_time = Comm.downlink_frames_duration(self.downlink_frames_count(), bitrate)
        return Comm.downlink_energy_consumption(transmission_time)

    @classmethod
    def energy_consumption(self, bitrate):
        return self.payload_energy_consumption() + self.downlink_energy_consumption(bitrate)

    @classmethod
    def energy_consumptions(self):
        energy_1200 = float(self.energy_consumption(1200))
        energy_2400 = float(self.energy_consumption(2400))
        energy_4800 = float(self.energy_consumption(4800))
        energy_9600 = float(self.energy_consumption(9600))
        return Energys([energy_1200, energy_2400, energy_4800, energy_9600])

    @classmethod
    def downlink_frames_count(self):
        return self.data_file_frames_count() + self.photo_frames_count()

    @classmethod
    def downlink_durations(self):
        return Comm.downlink_durations(self.downlink_frames_count())
