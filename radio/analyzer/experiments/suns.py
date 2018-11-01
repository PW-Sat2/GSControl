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

# SunS

"""
Active components:
* SunS Exp
* SunS Ref
* Gyroscope - does not count to additional power consumption since it's turned on all the time
* PLD SENS

"""

SUNS_EXP_AVERAGE_POWER_3V3 = 0.0701  # W (source: https://team.pw-sat.pl/w/suns/suns_fm/power_consumption/)
SUNS_REF_AVERAGE_POWER_5V0 = 0.05  # W (source: datasheet)
PLD_SENS_AVERAGE_POWER_5V0 = 5.0*0.0243  # W (source: https://team.pw-sat.pl/w/system/power-budget/experiments/#payload-commisioning - PLD SENS @ idle state)


"""
Experiment task:

begin_experimet()

for i in range(qty_of_sampling_sessions):
    turn_on_equipment();
    delay_seconds(3)

    for j in range(samples_qty):
        take_sample_from_all_sensors()
        delay_seconds(short_delay)
    turn_off_equipment();
    
    delay_decaseconds(long_delay)

end_experiment()

"""

EQUIPMENT_TURN_ON_TIME = 3  # s
ESTIMATED_OBC_DELAY_PER_SAMPLE = 0.01  # s


def itime_to_suns_measurement_time(itime):
    return 0.0026*itime + 0.019


def equipment_active_time(itime, samples_qty, short_delay, qty_of_sampling_sessions):
    return EQUIPMENT_TURN_ON_TIME*qty_of_sampling_sessions + (itime_to_suns_measurement_time(itime) +
           ESTIMATED_OBC_DELAY_PER_SAMPLE + short_delay)*samples_qty*qty_of_sampling_sessions


def experiment_time(itime, samples_qty, short_delay, long_delay, qty_of_sampling_sessions):
    return equipment_active_time(itime, samples_qty, short_delay, qty_of_sampling_sessions) + long_delay*qty_of_sampling_sessions*10


def energy_consumption(itime, samples_qty, short_delay, long_delay, qty_of_sampling_sessions):
    return (SUNS_EXP_AVERAGE_POWER_3V3/EFFICIENCY_3V3 + SUNS_REF_AVERAGE_POWER_5V0/EFFICIENCY_5V0 +
            PLD_SENS_AVERAGE_POWER_5V0/EFFICIENCY_5V0) *\
            equipment_active_time(itime, samples_qty, short_delay, qty_of_sampling_sessions)/3600.0


def storage_usage(samples_qty, qty_of_sampling_sessions):
    PRIMARY_DATA_SET = 67  # bytes (source: https://team.pw-sat.pl/w/oper/mission_plan/suns_experiment/#the-primary-and-secondar)
    SECONDARY_DATA_SET = 34  # bytes (source: https://team.pw-sat.pl/w/oper/mission_plan/suns_experiment/#the-primary-and-secondar)

    padding_primary = samples_qty * qty_of_sampling_sessions / 3 * 17 * 2.1  # z dupy
    padding_secondary = samples_qty * qty_of_sampling_sessions / 6 * 14 * 2.4  # z dupy

    primary_file = int(math.ceil((PRIMARY_DATA_SET*samples_qty*qty_of_sampling_sessions + padding_primary)/FILE_FRAME_PAYLOAD))
    secondary_file = int(math.ceil((SECONDARY_DATA_SET*samples_qty*qty_of_sampling_sessions + padding_secondary)/FILE_FRAME_PAYLOAD))

    return primary_file, secondary_file


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
    print "Equipment active time:", equipment_active_time(100, 15, 2, 10), "s"
    print "Experiment duration:", experiment_time(100, 15, 2, 24, 10), "s"
    print "Energy consumption from BP:", energy_consumption(10, 15, 2, 24, 10), "Wh"
    print "Storage usage (primary, secondary):", storage_usage(20, 20), "frames"
    print "TX time (primary, secondary files):", comm_transmission_time(storage_usage(20, 20)[0]), comm_transmission_time(storage_usage(20, 20)[1]), "s"
    print "TX power usage (primary, secondary files):", comm_energy_usage(comm_transmission_time(storage_usage(20, 20)[0])), comm_energy_usage(comm_transmission_time(storage_usage(20, 20)[1])), "Wh"
