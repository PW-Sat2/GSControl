import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *


class RadfetExperimentParameters:
    CORRELATION_ID_OFFSET = 0
    DELAY_OFFSET = 1
    SAMPLES_COUNT_OFFSET = 2

    def __init__(self, frame_payload):
        self.correlation_id = self.get_parameters(frame_payload)[self.CORRELATION_ID_OFFSET]
        self.delay = self.get_parameters(frame_payload)[self.DELAY_OFFSET]
        self.samples_count = self.get_parameters(frame_payload)[self.SAMPLES_COUNT_OFFSET]

    @classmethod
    def get_parameters(self, frame_payload):
        END_OF_PARAMS_OFFSET = 3
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


class RadfetExperiment:
    def __init__(self, frame_payload):
        self.parameters = RadfetExperimentParameters(frame_payload)

    @classmethod
    def experiment_duration(self, parameters):
        RADFET_SAMPLIG_TIME = 25  # s (around, source @mgumiela)
        OBC_EXP_STARTUP_DELAY = 3  # s (source: OBC code)

        return OBC_EXP_STARTUP_DELAY + parameters.delay * 10 + parameters.samples_count * RADFET_SAMPLIG_TIME

    def task_duration(self):
        return Duration(self.experiment_duration(self.parameters))

    @classmethod
    def experiment_energy_consumption(self, parameters):
        return Energy((self.experiment_duration(parameters) * (Radfet.RADFET_MEAN_POWER_5V0 + Radfet.SUNS_REF_AVERAGE_POWER_5V0)\
            / Eps.EFFICIENCY_5V0 / 3600.0) * 1000.0)

    def energy_consumptions(self):
        energy_1200 = float(self.experiment_energy_consumption(self.parameters) + self.downlink_energy_consumption(1200, self.parameters))
        energy_2400 = float(self.experiment_energy_consumption(self.parameters) + self.downlink_energy_consumption(2400, self.parameters))
        energy_4800 = float(self.experiment_energy_consumption(self.parameters) + self.downlink_energy_consumption(4800, self.parameters))
        energy_9600 = float(self.experiment_energy_consumption(self.parameters) + self.downlink_energy_consumption(9600, self.parameters))
        return Energys([energy_1200, energy_2400, energy_4800, energy_9600])

    @classmethod
    def downlink_energy_consumption(self, bitrate, parameters):
        transmission_time = Comm.downlink_frames_duration(self.experiment_files_frames_count(parameters), bitrate)
        return Comm.downlink_energy_consumption(transmission_time)

    @classmethod
    def experiment_files_frames_count(self, parameters):
        DATA_POINT_SIZE = 34
        return (parameters.samples_count + 2) * DATA_POINT_SIZE / Comm.FULL_FRAME  # z dupy

    def downlink_frames_count(self):
        return self.experiment_files_frames_count(self.parameters)

    def storage_usage(self):
        return Storage((self.experiment_files_frames_count(self.parameters) * Comm.FULL_FRAME) / 1024.0)

    def downlink_durations(self):
        return Comm.downlink_durations(self.downlink_frames_count())
