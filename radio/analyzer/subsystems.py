import math
from resources import *


class Eps:
    EFFICIENCY_3V3 = 0.7
    EFFICIENCY_5V0 = 0.7


class Obc:
    FILE_FRAME_PAYLOAD = 232  # bytes (source: https://team.pw-sat.pl/w/obc/frames_format/)


class Comm:
    DOWNLINK_POWER_CONSUMPTION = 3.0  # W
    DOWNLINK_MAX_PREAMBLE = Duration(0.4)
    DOWNLINK_MAX_PREAMBLE_9600 = Duration(0.3)
    UPLINK_PTT_DELAY = Duration(1.0)
    FULL_FRAME = 235  # bytes

    @classmethod
    def downlink_frames_duration(self, frames_count, bitrate):
        single_preamble = self.DOWNLINK_MAX_PREAMBLE
        if bitrate == 9600:
            single_preamble = self.DOWNLINK_MAX_PREAMBLE_9600

        preambles_duration = Duration(math.ceil(frames_count / 10) * float(single_preamble))

        duration = Duration(frames_count * (Comm.FULL_FRAME * 8) / bitrate)
        return duration + preambles_duration

    @classmethod
    def downlink_bytes_duration(self, bytes_count, bitrate):
        bits_count = (bytes_count) * 8
        tx_preamble = self.DOWNLINK_MAX_PREAMBLE
        if bitrate == 9600:
            tx_preamble = self.DOWNLINK_MAX_PREAMBLE_9600
        return Duration(float(bits_count) / bitrate) + tx_preamble

    @classmethod
    def downlink_durations(self, frames_count):
        duration_1200 = float(self.downlink_frames_duration(frames_count, 1200))
        duration_2400 = float(self.downlink_frames_duration(frames_count, 2400))
        duration_4800 = float(self.downlink_frames_duration(frames_count, 4800))
        duration_9600 = float(self.downlink_frames_duration(frames_count, 9600))
        return Durations([duration_1200, duration_2400, duration_4800, duration_9600])

    @classmethod
    def downlink_energy_consumption(self, duration):
        return Energy((self.DOWNLINK_POWER_CONSUMPTION * float(duration) / 3600.0) * 1000.0)

    @classmethod
    def uplink_bytes_duration(self, bytes_count, bitrate):
        bits_count = bytes_count * 8
        return Duration(float(bits_count) / bitrate) + self.UPLINK_PTT_DELAY


class Cam:
    PHOTO_128_MAX_FULL_FRAMES = 12 # in FULL FRAMES
    PHOTO_240_MAX_FULL_FRAMES = 20 # in FULL FRAMES
    PHOTO_480_MAX_FULL_FRAMES = 80 # in FULL FRAMES

class Pld:
    '''
    Resources utilization for Payload Commissioning.

    Source: PWSat2-SVN/system/tests_and_reports/29 -
            Experiments power consumption estimation/data/plots
    '''

    SENS_5V0_ENERGY_CONSUMPTION = 0.0021 # Wh
    PLD_3V3_ENERGY_CONSUMPTION = 0.0178 # Wh
