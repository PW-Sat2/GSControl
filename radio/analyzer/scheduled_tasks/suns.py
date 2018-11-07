import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *


class SunsExperiment:
    @classmethod
    def itime_to_suns_measurement_time(self, itime):
        return 0.0026*itime + 0.019

    @classmethod
    def equipment_active_time(self, itime, samples_qty, short_delay, qty_of_sampling_sessions):
        return Suns.EQUIPMENT_TURN_ON_TIME*qty_of_sampling_sessions + (self.itime_to_suns_measurement_time(itime) +
            Suns.ESTIMATED_OBC_DELAY_PER_SAMPLE + short_delay)*samples_qty*qty_of_sampling_sessions

    @classmethod
    def task_duration(self, itime, samples_qty, short_delay, long_delay, qty_of_sampling_sessions):
        return self.equipment_active_time(itime, samples_qty, short_delay, qty_of_sampling_sessions) + long_delay*qty_of_sampling_sessions*10


    @classmethod
    def energy_consumption(self, itime, samples_qty, short_delay, long_delay, qty_of_sampling_sessions):
        return (Suns.SUNS_EXP_AVERAGE_POWER_3V3/Eps.EFFICIENCY_3V3 + Suns.SUNS_REF_AVERAGE_POWER_5V0/Eps.EFFICIENCY_5V0 +
                Suns.PLD_SENS_AVERAGE_POWER_5V0/Eps.EFFICIENCY_5V0) *\
                self.equipment_active_time(itime, samples_qty, short_delay, qty_of_sampling_sessions)/3600.0

    @classmethod
    def storage_usage(samples_qty, qty_of_sampling_sessions):
        # bytes (source: https://team.pw-sat.pl/w/oper/mission_plan/suns_experiment/#the-primary-and-secondar)
        PRIMARY_DATA_SET = 67
        SECONDARY_DATA_SET = 34  

        padding_primary = samples_qty * qty_of_sampling_sessions / 3 * 17 * 2.1  # z dupy
        padding_secondary = samples_qty * qty_of_sampling_sessions / 6 * 14 * 2.4  # z dupy

        primary_file = int(math.ceil((PRIMARY_DATA_SET*samples_qty*qty_of_sampling_sessions + padding_primary)/Comm.FULL_FRAME))
        secondary_file = int(math.ceil((SECONDARY_DATA_SET*samples_qty*qty_of_sampling_sessions + padding_secondary)/Comm.FULL_FRAME))

        return primary_file, secondary_file
