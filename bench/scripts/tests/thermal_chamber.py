from bench_init import *

import time, datetime
from tools.log import CSVLogger
import progressbar

class RadFET(object):
    def _init_(self, filename_base):
        self.logger = CSVLogger(filename_base + "_radfet", in_test=True)

    def log(self):
        radfet_data = obc.payload_radfet_read()
        temps_data = obc.payload_temps()
        self.logger.log({"timestamp": time.time()}, radfet_data, temps_data)


class SunS(object):
    def _init_(self, filename_base):
        self.logger = CSVLogger(filename_base + "_suns", in_test=True)
        self.suns_keys = ["status 1 ack", "status 2 presence", "status 3 adc_valid", "ALS_1_A_VL", "ALS_1_B_VL", "ALS_1_C_VL", "ALS_1_D_VL", "ALS_2_A_VL", "ALS_2_B_VL", "ALS_2_C_VL", "ALS_2_D_VL", "ALS_3_A_VL", "ALS_3_B_VL", "ALS_3_C_VL", "ALS_3_D_VL", "temp str", "rtd A", "rtd B", "rtd C", "rtd D", "gain", "itime", "ALS_1_A_IR", "ALS_1_B_IR", "ALS_1_C_IR", "ALS_1_D_IR", "ALS_2_A_IR", "ALS_2_B_IR", "ALS_2_C_IR", "ALS_2_D_IR", "ALS_3_A_IR", "ALS_3_B_IR", "ALS_3_C_IR", "ALS_3_D_IR"]

    def log(self, gain, itime):
        suns_raw_data = obc.measure_suns(gain, itime)
        temps_data = obc.payload_temps()

        suns_data = dict(zip(self.suns_keys, suns_raw_data))
        self.logger.log({"timestamp": time.time()}, suns_data)


class EPS(object):
    def _init_(self, filename_base):
        self.logger_a = CSVLogger(filename_base + "_eps_a", in_test=True)
        self.logger_b = CSVLogger(filename_base + "_eps_b", in_test=True)
        self.hk_a_keys = ["MPPT_X SOL_VOLT", "MPPT_X SOL_CURR", "MPPT_X SOL_OUT_VOLT", "MPPT_X TEMP", "MPPT_X STATE", "MPPT_Y_PLUS SOL_VOLT", "MPPT_Y_PLUS SOL_CURR", "MPPT_Y_PLUS SOL_OUT_VOLT", "MPPT_Y_PLUS TEMP", "MPPT_Y_PLUS STATE", "MPPT_Y_MINUS SOL_VOLT", "MPPT_Y_MINUS SOL_CURR", "MPPT_Y_MINUS SOL_OUT_VOLT", "MPPT_Y_MINUS TEMP", "MPPT_Y_MINUS STATE", "DISTR VOLT_3V3", "DISTR CURR_3V3", "DISTR VOLT_5V", "DISTR CURR_5V", "DISTR VOLT_VBAT", "DISTR CURR_VBAT", "DISTR LCL_STATE", "DISTR LCL_FLAGB", "BATC_A VOLT_A", "BATC_A CHRG_CURR", "BATC_A DCHRG_CURR", "BATC_A TEMP", "BATC_A STATE", "BP_A TEMP_A", "BP_A TEMP_B", "CTRLB VOLT_3V3d", "CTRLA SAFETY_CTR", "CTRLA PWR_CYCLES", "CTRLA UPTIME", "CTRLA TEMP", "CTRLA SUPP_TEMP", "DCDC3V3 TEMP", "DCDC5V TEMP"]
        self.hk_b_keys = ["BP_B TEMP_C", "BATC_B VOLT_B", "CTRLB VOLT_3V3d", "CTRLA SAFETY_CTR", "CTRLA PWR_CYCLES", "CTRLA UPTIME", "CTRLA TEMP", "CTRLA SUPP_TEMP"]

    def log(self):
        hk_a = obc.read_housekeeping_a()
        hk_a_values = [hk_a.MPPT_X.SOL_VOLT, hk_a.MPPT_X.SOL_CURR, hk_a.MPPT_X.SOL_OUT_VOLT, hk_a.MPPT_X.TEMP, hk_a.MPPT_X.STATE, hk_a.MPPT_Y_PLUS.SOL_VOLT, hk_a.MPPT_Y_PLUS.SOL_CURR, hk_a.MPPT_Y_PLUS.SOL_OUT_VOLT, hk_a.MPPT_Y_PLUS.TEMP, hk_a.MPPT_Y_PLUS.STATE, hk_a.MPPT_Y_MINUS.SOL_VOLT, hk_a.MPPT_Y_MINUS.SOL_CURR, hk_a.MPPT_Y_MINUS.SOL_OUT_VOLT, hk_a.MPPT_Y_MINUS.TEMP, hk_a.MPPT_Y_MINUS.STATE, hk_a.DISTR.VOLT_3V3, hk_a.DISTR.CURR_3V3, hk_a.DISTR.VOLT_5V, hk_a.DISTR.CURR_5V, hk_a.DISTR.VOLT_VBAT, hk_a.DISTR.CURR_VBAT, hk_a.DISTR.LCL_STATE, hk_a.DISTR.LCL_FLAGB, hk_a.BATC.VOLT_A, hk_a.BATC.CHRG_CURR, hk_a.BATC.DCHRG_CURR, hk_a.BATC.TEMP, hk_a.BATC.STATE, hk_a.BP.TEMP_A, hk_a.BP.TEMP_B, hk_a.CTRLB.VOLT_3V3d, hk_a.CTRLA.SAFETY_CTR, hk_a.CTRLA.PWR_CYCLES, hk_a.CTRLA.UPTIME, hk_a.CTRLA.TEMP, hk_a.CTRLA.SUPP_TEMP, hk_a.DCDC3V3.TEMP, hk_a.DCDC5V.TEMP]
        hk_a_dict = dict(zip(self.hk_a_keys, hk_a_values))
        self.logger_a.log({"timestamp": time.time()}, hk_a_dict)

        hk_b = obc.read_housekeeping_b()
        hk_b_values = [hk_b.BP.TEMP_C, hk_b.BATC.VOLT_B, hk_b.CTRLA.VOLT_3V3d, hk_b.CTRLB.SAFETY_CTR, hk_b.CTRLB.PWR_CYCLES, hk_b.CTRLB.UPTIME, hk_b.CTRLB.TEMP, hk_b.CTRLB.SUPP_TEMP]
        hk_b_dict = dict(zip(self.hk_b_keys, hk_b_values))
        self.logger_b.log({"timestamp": time.time()}, hk_b_dict)


class Gyro(object):
    def _init_(self, filename_base):
        self.logger = CSVLogger(filename_base + "_gyro", in_test=True)
        self.gyro_keys = ["X", "Y", "Z", "Temperature"]
        obc.gyro_init()

    def log(self, gain, itime):
        gyro_raw_data = obc.gyro_read()
        temps_data = obc.payload_temps()

        gyro_data = dict(zip(self.gyro_keys, gyro_raw_data))
        self.logger.log({"timestamp": time.time()}, gyro_data)


class Photo(object):
    def _init_(self, filename_base):
        self.filename_base = filename_base
        self.wing_filename = 'wing'
        self.nadir_filename = 'nadir'
        self.last_photo_finished = True

    def take_photo(self):
        if self.last_photo_finished is True or (self.last_photo_time + 300) < time.time():
            self.last_photo_time = time.time()
            send(tc.camera.TakePhoto(tc.camera.CameraLocation.Nadir, tc.camera.PhotoResolution.p128, 1, tc.camera.timedelta(0), self.nadir_filename))
            send(tc.camera.TakePhoto(tc.camera.CameraLocation.Wing, tc.camera.PhotoResolution.p128, 1, tc.camera.timedelta(0), self.wing_filename))
            self.last_photo_finished = False

    def get_if_ready(self):
        file_list = obc.list_files('/')
        if self.nadir_filename + '_0' in file_list:
            print("Nadir ready")
            with open(self.filename_base + '_nadir_' + str(self.last_photo_time), 'wb') as f:
                f.write(obc.read_file(self.nadir_filename + '_0'))
            obc.remove_file(self.nadir_filename + '_0')
            self.last_photo_finished = True
        else:
            print("Nadir not ready")
            self.last_photo_finished = False

        if self.wing_filename + '_0' in file_list:
            print("Wing ready")
            with open(self.filename_base + '_wing_' + str(self.last_photo_time), 'wb') as f:
                f.write(obc.read_file(self.wing_filename + '_0'))
            obc.remove_file(self.wing_filename + '_0')
            self.last_photo_finished = True
        else:
            print("Wing not ready")
            self.last_photo_finished = False


@make_test
def climatic_chamber_calibration(duration, filename_base, suns_gain, suns_itime):
    bar = progressbar.ProgressBar(max_value=duration.total_seconds()/60)

    radfet = RadFET(filename_base)
    suns = SunS(filename_base)
    eps = EPS(filename_base)
    gyro = Gyro(filename_base)
    photo = Photo(filename_base)
    

    PrintLog("Check if OBC Terminal is available")
    PrintLog(obc.ping())

    PrintLog("Be sure that no experiment is currently running")
    tm.assert_equal(tm.OBC.Experiments.Code, 'None')

    PrintLog("enable PLD LCL")
    PrintLog(obc.enable_lcl(5))

    PrintLog("enable SunS LCL")
    PrintLog(obc.enable_lcl(2))
    time.sleep(5)

    PrintLog("enable radfet lcl")
    PrintLog(obc.payload_radfet_on())

    start_time = time.time()
    stop_time = start_time + duration.total_seconds()

    PrintLog("Stop time: " + str(datetime.datetime.fromtimestamp(stop_time)))

    while time.time() < stop_time:
        photo.take_photo()
        suns.log(suns_gain, suns_itime)
        eps.log()
        gyro.log()
        radfet.log()
        photo.get_if_ready()

        try:
            bar.update(round((time.time()-start_time)/60, 2))
        except ValueError:
            pass

    PrintLog("disable radfet LCL")
    PrintLog(obc.payload_radfet_off())

    PrintLog("disable PLD LCL")
    PrintLog(obc.disable_lcl(5))

    PrintLog("disable SunS LCL")
    PrintLog(obc.disable_lcl(2))
