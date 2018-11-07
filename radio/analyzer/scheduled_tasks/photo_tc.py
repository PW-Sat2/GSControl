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


PHOTO_128_TIME = 1.25  # s (max. val, about 25% greater than min)
PHOTO_240_TIME = 4.7   # s (max. val, about 25% greater than min)
PHOTO_480_TIME = 19    # s (max. val, about 25% greater than min)

CAM_POWER = 0.2618  # W (source: https://team.pw-sat.pl/w/cam/power_consumption/)


def photo_energy_consumption(resolution):
    if resolution == "p128":
        PHOTO_3V3_ENERGY_CONSUMPTION = PHOTO_128_TIME * CAM_POWER / 3600.0  # Wh
    elif resolution == "p240":
        PHOTO_3V3_ENERGY_CONSUMPTION = PHOTO_240_TIME * CAM_POWER / 3600.0  # Wh
    elif resolution == "p480":
        PHOTO_3V3_ENERGY_CONSUMPTION = PHOTO_480_TIME * CAM_POWER / 3600.0  # Wh

    return PHOTO_3V3_ENERGY_CONSUMPTION / EFFICIENCY_3V3


PHOTO_128_MAX_SIZE = 12  # z dupy
PHOTO_240_MAX_SIZE = 20  # z dupy
PHOTO_480_MAX_SIZE = 80  # z dupy


def photo_storage_usage(resolution):
    if resolution == "p128":
        PHOTO_STORAGE_USAGE = PHOTO_128_MAX_SIZE
    elif resolution == "p240":
        PHOTO_STORAGE_USAGE = PHOTO_240_MAX_SIZE
    elif resolution == "p480":
        PHOTO_STORAGE_USAGE = PHOTO_480_MAX_SIZE

    return PHOTO_STORAGE_USAGE


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


print "Energy usage (p128, p240, p480):", photo_energy_consumption("p128"), "Wh,", \
                                          photo_energy_consumption("p240"), "Wh,", \
                                          photo_energy_consumption("p480"), "Wh"

print "Storage usage (p128, p240, p480):", photo_storage_usage("p128"), "frames,", \
                                           photo_storage_usage("p240"), "frames,", \
                                           photo_storage_usage("p480"), "frames"

print "TX time (p128, p240, p480):", comm_transmission_time(photo_storage_usage("p128")), "s,",\
                                     comm_transmission_time(photo_storage_usage("p240")), "s,",\
                                     comm_transmission_time(photo_storage_usage("p480")), "s"

print "TX power usage (p128, p240, p480):", comm_energy_usage(comm_transmission_time(photo_storage_usage("p128"))), "Wh", \
                                            comm_energy_usage(comm_transmission_time(photo_storage_usage("p240"))), "Wh",\
                                            comm_energy_usage(comm_transmission_time(photo_storage_usage("p480"))), "Wh"
