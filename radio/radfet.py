import math

# EPS constants

EFFICIENCY_3V3 = 0.7  # (source: @pkuligowski)
EFFICIENCY_5V0 = 0.7  # (source: @pkuligowski)


# OBC constants

FILE_FRAME_PAYLOAD = 232  # bytes (source: https://team.pw-sat.pl/w/obc/frames_format/)


# COMM constants

TX_POWER_CONSUMPTION = 3  # W
TX_MAX_PREAMBLE = 0.4  # s
FULL_FRAME = 235  # bytes

# RadFET

RADFET_MEAN_POWER_5V0 = 0.2  # W (source PWSat2-SVN\system\tests_and_reports\23 - Power budget measurements\payload\SENS_5V)
SUNS_REF_AVERAGE_POWER_5V0 = 0.05  # W (source: datasheet)

"""
Equipment active time: 373.35 s
Experiment duration: 2773.35 s
Energy consumption from BP: 0.032429047619 Wh
Storage usage (primary, secondary): (136, 69) frames
TX time (primary, secondary files): {1200: 218.27, 2400: 111.73, 9600: 31.83, 4800: 58.47} {1200: 110.5, 2400: 56.45, 9600: 15.91, 4800: 29.42} s
TX power usage (primary, secondary files): 0.0487 0.0245 Wh
"""


def radfet_experiment_duration(delay, samples_count):
    RADFET_SAMPLIG_TIME = 25  # s (around, source @mgumiela)
    OBC_EXP_STARTUP_DELAY = 3  # s (source: OBC code)

    return OBC_EXP_STARTUP_DELAY + delay * 10 + samples_count * RADFET_SAMPLIG_TIME


def radfet_experiment_energy_consumption(delay, samples_count):
    return radfet_experiment_duration(delay, samples_count) * (RADFET_MEAN_POWER_5V0 + SUNS_REF_AVERAGE_POWER_5V0)\
           / EFFICIENCY_5V0 / 3600.0


def radfet_storage_usage(samples_count):
    DATA_POINT_SIZE = 34
    return (samples_count + 2) * DATA_POINT_SIZE / FILE_FRAME_PAYLOAD  # z dupy


def comm_transmission_time(full_frames_qty):
    preambles_time = math.ceil(full_frames_qty/10)*TX_MAX_PREAMBLE
    time_1200 = round(full_frames_qty * (FULL_FRAME * 8)/1200.0 + preambles_time, 2)
    time_2400 = round(full_frames_qty * (FULL_FRAME * 8) / 2400.0 + preambles_time, 2)
    time_4800 = round(full_frames_qty * (FULL_FRAME * 8) / 4800.0 + preambles_time, 2)
    time_9600 = round(full_frames_qty * (FULL_FRAME * 8) / 9600.0 + preambles_time, 2)

    return {1200: time_1200, 2400: time_2400, 4800: time_4800, 9600: time_9600}


def comm_energy_usage(transmission_time):
    comm_energy = {}
    for key in transmission_time:
        comm_energy[key] = round(TX_POWER_CONSUMPTION * transmission_time[key] / 3600.0, 4)
    return comm_energy


print "Experiment duration:", radfet_experiment_duration(120, 255), "s"
print "Energy consumption from BP:", radfet_experiment_energy_consumption(120, 255), "Wh"
print "Storage usage:", radfet_storage_usage(255), "frames"
print "TX time:", comm_transmission_time(radfet_storage_usage(255)), "s"
print "TX power usage:", comm_energy_usage(comm_transmission_time(radfet_storage_usage(255))), "Wh"
