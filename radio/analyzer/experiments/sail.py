import math

# INFO: results are cross-checked with data from experiment:
# PWSat2-SVN\system\tests_and_reports\38 - Sail experiment radio

# EPS constants

EFFICIENCY_3V3 = 0.7  # (source: @pkuligowski)
EFFICIENCY_5V0 = 0.7  # (source: @pkuligowski)


# OBC constants

FILE_FRAME_PAYLOAD = 232  # bytes (source: https://team.pw-sat.pl/w/obc/frames_format/)


# COMM constants

TX_POWER_CONSUMPTION = 3  # W
TX_MAX_PREAMBLE = 0.4  # s
FULL_FRAME = 235  # bytes

# Sail

SUNS_REF_AVERAGE_POWER_5V0 = 0.05  # W (source: datasheet)
PLD_SENS_AVERAGE_POWER_5V0 = 5.0*0.0243  # W (source: https://team.pw-sat.pl/w/system/power-budget/experiments/#payload-commisioning - PLD SENS @ idle state)

SAIL_TK_POWER = 2  # W
CAMERA_POWER = 0.2618  # W


def sail_experiment_duration():
    SAIL_EXP_DURATION = 240  # s (source: OBC code)

    return SAIL_EXP_DURATION


def sail_experiment_energy_consumption():
    themal_knives_energy = 120 * 2 * SAIL_TK_POWER / 3600.0
    pld_board_energy = sail_experiment_duration() * (PLD_SENS_AVERAGE_POWER_5V0 + SUNS_REF_AVERAGE_POWER_5V0) / EFFICIENCY_5V0 / 3600.0
    cameras_energy = sail_experiment_duration() * 2 * CAMERA_POWER / EFFICIENCY_3V3 / 3600.0
    comm_energy = comm_energy_usage(comm_transmission_time(sail_data_file_storage_usage()))[1200]

    return themal_knives_energy + pld_board_energy + cameras_energy + comm_energy


PHOTO_128_MAX_SIZE = 12  # z dupy
PHOTO_240_MAX_SIZE = 20  # z dupy
PHOTO_480_MAX_SIZE = 80  # z dupy


def sail_data_file_storage_usage():
    return 22


def sail_photos_storage_usage():
    SMALL_PHOTO_QTY = 64
    FINAL_PHOTO_QTY = 2
    return PHOTO_128_MAX_SIZE * SMALL_PHOTO_QTY + FINAL_PHOTO_QTY * PHOTO_480_MAX_SIZE


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


if __name__ == '__main__':
    print "Experiment duration:", sail_experiment_duration(), "s"
    print "Energy consumption from BP:", sail_experiment_energy_consumption(), "Wh"
    print "Storage usage:", sail_data_file_storage_usage(), "frames,", sail_photos_storage_usage(), "frames"
    print "TX time - data file, photos:", comm_transmission_time(sail_data_file_storage_usage()), "s,",\
                                          comm_transmission_time(sail_photos_storage_usage()), "s"
    print "TX power usage - data file, photos:", comm_energy_usage(comm_transmission_time(sail_data_file_storage_usage())), "Wh,",\
                                                 comm_energy_usage(comm_transmission_time(sail_photos_storage_usage())), "Wh"
