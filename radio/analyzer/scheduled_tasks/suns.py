import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *


class SunsExperimentParameters:
    GAIN_OFFSET = 1
    ITIME_OFFSET = 2
    SAMPLES_COUNT_OFFSET = 3
    SHORT_DELAY_OFFSET = 4
    SAMPLING_SESSION_COUNT_OFFSET = 5
    LONG_DELAY_OFFSET = 6

    def __init__(self, frame_payload):
        self.gain = self.get_parameters(frame_payload)[self.GAIN_OFFSET]
        self.itime = self.get_parameters(frame_payload)[self.ITIME_OFFSET]
        self.samples_count = self.get_parameters(frame_payload)[self.SAMPLES_COUNT_OFFSET]
        self.short_delay = self.get_parameters(frame_payload)[self.SHORT_DELAY_OFFSET]
        self.sampling_session_count = self.get_parameters(frame_payload)[self.SAMPLING_SESSION_COUNT_OFFSET]
        self.long_delay = self.get_parameters(frame_payload)[self.LONG_DELAY_OFFSET]

    @classmethod
    def get_parameters(self, frame_payload):
        END_OF_PARAMS_OFFSET = 7
        END_OF_PATH_BYTE = 0

        experiment_params = []
        for index in range(0, END_OF_PARAMS_OFFSET):
            experiment_params.append(ord(frame_payload[index]))

        experiment_path = ""
        for index in range(END_OF_PARAMS_OFFSET, len(frame_payload)):
            if ord(frame_payload[index]) == END_OF_PATH_BYTE:
                break
            experiment_path = experiment_path + frame_payload[index]

        experiment_params.append(experiment_path)
        return experiment_params


class SunsExperiment:
    def __init__(self, frame_payload):
        self.parameters = SunsExperimentParameters(frame_payload)

    def task_duration(self):
        return Duration(self.equipment_active_time(self.parameters) + self.parameters.long_delay * self.parameters.sampling_session_count * 10)

    def storage_usage(self):
        return Storage((self.experiment_files_frames_count(self.parameters) * Comm.FULL_FRAME) / 1024.0)

    def energy_consumptions(self):
        energy_1200 = float(self.payload_energy_consumption(self.parameters) + self.downlink_energy_consumption(1200, self.parameters))
        energy_2400 = float(self.payload_energy_consumption(self.parameters) + self.downlink_energy_consumption(2400, self.parameters))
        energy_4800 = float(self.payload_energy_consumption(self.parameters) + self.downlink_energy_consumption(4800, self.parameters))
        energy_9600 = float(self.payload_energy_consumption(self.parameters) + self.downlink_energy_consumption(9600, self.parameters))
        return Energys([energy_1200, energy_2400, energy_4800, energy_9600])

    def downlink_frames_count(self):
        return self.experiment_files_frames_count(self.parameters)

    def downlink_durations(self):
        return Comm.downlink_durations(self.downlink_frames_count())

    @classmethod
    def itime_to_suns_measurement_time(self, itime):
        return 0.0026*itime + 0.019

    @classmethod
    def equipment_active_time(self, parameters):
        return Suns.EQUIPMENT_TURN_ON_TIME * parameters.sampling_session_count + (self.itime_to_suns_measurement_time(parameters.itime) +
            Suns.ESTIMATED_OBC_DELAY_PER_SAMPLE + parameters.short_delay) * parameters.samples_count * parameters.sampling_session_count

    @classmethod
    def payload_energy_consumption(self, parameters):
        return Energy(((Suns.SUNS_EXP_AVERAGE_POWER_3V3 / Eps.EFFICIENCY_3V3 + Suns.SUNS_REF_AVERAGE_POWER_5V0 / Eps.EFFICIENCY_5V0 +
                Suns.PLD_SENS_AVERAGE_POWER_5V0 / Eps.EFFICIENCY_5V0) * self.equipment_active_time(parameters) / 3600.0) * 1000.0)

    @classmethod
    def downlink_energy_consumption(self, bitrate, parameters):
        transmission_time = Comm.downlink_frames_duration(self.experiment_files_frames_count(parameters), bitrate)
        return Comm.downlink_energy_consumption(transmission_time)

    @classmethod
    def experiment_files_frames_count(self, parameters):
        # bytes (source: https://team.pw-sat.pl/w/oper/mission_plan/suns_experiment/#the-primary-and-secondar)
        PRIMARY_DATA_SET = 67
        SECONDARY_DATA_SET = 34  

        padding_primary = parameters.samples_count * parameters.sampling_session_count / 3 * 17 * 2.1
        padding_secondary = parameters.samples_count * parameters.sampling_session_count / 6 * 14 * 2.4

        primary_file = int(math.ceil((PRIMARY_DATA_SET * parameters.samples_count * parameters.sampling_session_count + padding_primary) / Comm.FULL_FRAME))
        secondary_file = int(math.ceil((SECONDARY_DATA_SET * parameters.samples_count * parameters.sampling_session_count + padding_secondary) / Comm.FULL_FRAME))

        return primary_file + secondary_file
