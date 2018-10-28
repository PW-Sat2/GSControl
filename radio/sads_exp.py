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


def sads_experiment_duration():
    SADS_EXP_DURATION = 290  # s (source: PWSat2-SVN\system\tests_and_reports\39 - SADS with load)

    return SADS_EXP_DURATION


def sads_experiment_energy_consumption():
    SADS_ENERGY_CONSUMPTION = 0.1293  # Wh (source: PWSat2-SVN\system\tests_and_reports\39 - SADS with load)
    return SADS_ENERGY_CONSUMPTION


def sads_data_file_storage_usage():
    return 21


PHOTO_480_MAX_SIZE = 80  # z dupy


def sads_photo_storage_usage():
    return PHOTO_480_MAX_SIZE


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


print "Experiment duration:", sads_experiment_duration(), "s"
print "Energy consumption from BP:", sads_experiment_energy_consumption(), "Wh"
print "Storage usage:", sads_data_file_storage_usage(), "frames,", sads_photo_storage_usage(), "frames"
print "TX time - data file, photo:", comm_transmission_time(sads_data_file_storage_usage()), "s,",\
                                      comm_transmission_time(sads_photo_storage_usage()), "s"
print "TX power usage - data file, photo:", comm_energy_usage(comm_transmission_time(sads_data_file_storage_usage())), "Wh,",\
                                             comm_energy_usage(comm_transmission_time(sads_photo_storage_usage())), "Wh"