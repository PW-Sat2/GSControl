import time
import inspect
import nose.tools

from tools.tools import PrintLog


class TM(object):
    class OBC(object):
        class Startup(object):
            BootCounter = ['01: Startup', '0000: Boot Counter']
            BootIndex = ['01: Startup', '0032: Boot Index']
            BootReason = ['01: Startup', '0040: Boot Reason']

        CodeCRC = ['02: Program State', '0056: Program CRC']

        class Time(object):
            Mission = ['03: Time Telemetry', '0072: Mission time']
            External = ['03: Time Telemetry', '0136: External time']

        class ErrorCounter(object):
            COMM = ['04: Error Counters', '0168: Comm']
            EPS = ['04: Error Counters', '0176: EPS']
            RTC = ['04: Error Counters', '0184: RTC']
            IMTQ = ['04: Error Counters', '0192: IMTQ']
            FLASH_1 = ['04: Error Counters', '0200: N25Q1']
            FLASH_2 = ['04: Error Counters', '0208: N25Q2']
            FLASH_3 = ['04: Error Counters', '0216: N25Q3']
            FLASH = ['04: Error Counters', '0224: N25q TMR']
            FRAM = ['04: Error Counters', '0232: FRAM TMR']
            PLD = ['04: Error Counters', '0240: Payload']
            CAM = ['04: Error Counters', '0248: Camera']
            SUNS = ['04: Error Counters', '0256: ExpSuns']
            ANTs_Primary = ['04: Error Counters', '0264: ANT Primary']
            ANTs_Secondary = ['04: Error Counters', '0272: ANT Backup']

        class Scrubbing(object):
            Primary = ['05: Scrubbing State', '0280: Primary Flash Scrubbing pointer']
            Secondary = ['05: Scrubbing State', '0283: Secondary Flash Scrubbing pointer']
            RAM = ['05: Scrubbing State', '0286: RAM Scrubbing pointer']

        Uptime = ['06: System', '0318: Uptime']
        FLASH_FreeSpace = ['07: File System', '0340: Free Space']
        SailDeployed = ['12: GPIO', '0780: Sail Deployed']
        Temperature = ['13: MCU', '0781: Temperature']

        class Experiments(object):
            Code = ['09: Experiments', '0490: Current experiment code']
            StartupResult = ['09: Experiments', '0494: Experiment Startup Result']
            LastIterationStatus = ['09: Experiments', '0502: Last Experiment Iteration Status']

    class ANT(object):
        class A(object):
            class First(object):
                Switch = ['08: Antenna', '0372: Antenna 1 Deployment Switch Ch A']
                LastStopDueToTime = ['08: Antenna', '0380: Antenna 1 Time Limit Reached Ch A']
                BurnActive = ['08: Antenna', '0388: Antenna 1 Burn Active Ch A']
                Counter = ['08: Antenna', '0402: Antenna 1 Activation Count Ch A']
                Time = ['08: Antenna', '0426: Antenna 1 Activation Time Ch A']

            class Second(object):
                Switch = ['08: Antenna', '0373: Antenna 2 Deployment Switch Ch A']
                LastStopDueToTime = ['08: Antenna', '0381: Antenna 2 Time Limit Reached Ch A']
                BurnActive = ['08: Antenna', '0389: Antenna 2 Burn Active Ch A']
                Counter = ['08: Antenna', '0405: Antenna 2 Activation Count Ch A']
                Time = ['08: Antenna', '0434: Antenna 2 Activation Time Ch A']

            class Third(object):
                Switch = ['08: Antenna', '0374: Antenna 3 Deployment Switch Ch A']
                LastStopDueToTime = ['08: Antenna', '0382: Antenna 3 Time Limit Reached Ch A']
                BurnActive = ['08: Antenna', '0390: Antenna 3 Burn Active Ch A']
                Counter = ['08: Antenna', '0408: Antenna 3 Activation Count Ch A']
                Time = ['08: Antenna', '0442: Antenna 3 Activation Time Ch A']

            class Fourth(object):
                Switch = ['08: Antenna', '0375: Antenna 4 Deployment Switch Ch A']
                LastStopDueToTime = ['08: Antenna', '0383: Antenna 4 Time Limit Reached Ch A']
                BurnActive = ['08: Antenna', '0391: Antenna 4 Burn Active Ch A']
                Counter = ['08: Antenna', '0411: Antenna 4 Activation Count Ch A']
                Time = ['08: Antenna', '0450: Antenna 4 Activation Time Ch A']

            SystemIndependentBurn = ['08: Antenna', '0396: System Independent Burn Ch A']
            IgnoringSwitches = ['08: Antenna', '0398: Ignoring Switches Ch A']
            Armed = ['08: Antenna', '0400: Armed Ch A']

        class B(object):
            class First(object):
                Switch = ['08: Antenna', '0376: Antenna 1 Deployment Switch Ch B']
                LastStopDueToTime = ['08: Antenna', '0384: Antenna 1 Time Limit Reached Ch B']
                BurnActive = ['08: Antenna', '0392: Antenna 1 Burn Active Ch B']
                Counter = ['08: Antenna', '0414: Antenna 1 Activation Count Ch B']
                Time = ['08: Antenna', '0458: Antenna 1 Activation Time Ch B']

            class Second(object):
                Switch = ['08: Antenna', '0377: Antenna 2 Deployment Switch Ch B']
                LastStopDueToTime = ['08: Antenna', '0385: Antenna 2 Time Limit Reached Ch B']
                BurnActive = ['08: Antenna', '0393: Antenna 2 Burn Active Ch B']
                Counter = ['08: Antenna', '0417: Antenna 2 Activation Count Ch B']
                Time = ['08: Antenna', '0466: Antenna 2 Activation Time Ch B']

            class Third(object):
                Switch = ['08: Antenna', '0378: Antenna 3 Deployment Switch Ch B']
                LastStopDueToTime = ['08: Antenna', '0386: Antenna 3 Time Limit Reached Ch B']
                BurnActive = ['08: Antenna', '0394: Antenna 3 Burn Active Ch B']
                Counter = ['08: Antenna', '0420: Antenna 3 Activation Count Ch B']
                Time = ['08: Antenna', '0474: Antenna 3 Activation Time Ch B']

            class Fourth(object):
                Switch = ['08: Antenna', '0379: Antenna 4 Deployment Switch Ch B']
                LastStopDueToTime = ['08: Antenna', '0387: Antenna 4 Time Limit Reached Ch B']
                BurnActive = ['08: Antenna', '0395: Antenna 4 Burn Active Ch B']
                Counter = ['08: Antenna', '0423: Antenna 4 Activation Count Ch B']
                Time = ['08: Antenna', '0482: Antenna 4 Activation Time Ch B']

            SystemIndependentBurn = ['08: Antenna', '0397: System Independent Burn Ch B']
            IgnoringSwitches = ['08: Antenna', '0399: Ignoring Switches Ch B']
            Armed = ['08: Antenna', '0401: Armed Ch B']

    class GYRO(object):
        X = ['10: Gyroscope', '0510: X measurement']
        Y = ['10: Gyroscope', '0526: Y measurement']
        Z = ['10: Gyroscope', '0542: Z measurement']
        Temperature = ['10: Gyroscope', '0558: Temperature']

    class COMM(object):
        class TX(object):
            Uptime = ['11: Comm', '0574: Transmitter Uptime']
            Bitrate = ['11: Comm', '0591: Transmitter Bitrate']
            PowerReflectedLast = ['11: Comm', '0593: [Last transmission] RF Reflected Power']
            TemperaturePowerAmplifierLast = ['11: Comm', '0605: [Last transmission] Power Amplifier Temperature']
            PowerForwardLast = ['11: Comm', '0617: [Last transmission] RF Forward Power']
            CurrentLast = ['11: Comm', '0629: [Last transmission] Transmitter Current']
            PowerForwardNow = ['11: Comm', '0641: [Now] RF Forward Power']
            CurrentNow = ['11: Comm', '0653: [Now] Transmitter Current']
            IdleState = ['11: Comm', '0665: Transmitter Idle State']
            BeaconState = ['11: Comm', '0666: Beacon State']
            TemperaturePowerAmplifierNow = ['11: Comm', '0756: [Now] Power Amplifier Temperature ']

        class RX(object):
            Uptime = ['11: Comm', '0667: Receiver Uptime']
            DopplerLast = ['11: Comm', '0684: [Last received] Doppler Offset']
            RSSILast = ['11: Comm', '0696: [Last received] RSSI']
            DopplerNow = ['11: Comm', '0708: [Now] Doppler Offset']
            Current = ['11: Comm', '0720: [Now] Receiver Current']
            SupplyVoltage = ['11: Comm', '0732: [Now] Power Supply Voltage']
            TemperatureOscillator = ['11: Comm', '0744: [Now] Oscillator Temperature']
            RSSINow = ['11: Comm', '0768: [Now] RSSI']

    class EPS(object):
        class A(object):
            class MPPT(object):
                class X(object):
                    SolarVoltage = ['14: Controller A', '0793: MPPT_X.SOL_VOLT']
                    SolarCurrent = ['14: Controller A', '0805: MPPT_X.SOL_CURR']
                    OutputVoltage = ['14: Controller A', '0817: MPPT_X.SOL_OUT_VOLT']
                    Temperature = ['14: Controller A', '0829: MPPT_X.Temperature']
                    State = ['14: Controller A', '0841: MPPT_X.State']

                class Y_Plus(object):
                    SolarVoltage = ['14: Controller A', '0844: MPPT_Y+.SOL_VOLT']
                    SolarCurrent = ['14: Controller A', '0856: MPPT_Y+.SOL_CURR']
                    OutputVoltage = ['14: Controller A', '0868: MPPT_Y+.SOL_OUT_VOLT']
                    Temperature = ['14: Controller A', '0880: MPPT_Y+.Temperature']
                    State = ['14: Controller A', '0892: MPPT_Y+.State']

                class Y_Minus(object):
                    SolarVoltage = ['14: Controller A', '0895: MPPT_Y-.SOL_VOLT']
                    SolarCurrent = ['14: Controller A', '0907: MPPT_Y-.SOL_CURR']
                    OutputVoltage = ['14: Controller A', '0919: MPPT_Y-.SOL_OUT_VOLT']
                    Temperature = ['14: Controller A', '0931: MPPT_Y-.Temperature']
                    State = ['14: Controller A', '0943: MPPT_Y-.State']

            class Distribution(object):
                Voltage3v3 = ['14: Controller A', '0946: DISTR.VOLT_3V3']
                Current3v3 = ['14: Controller A', '0956: DISTR.CURR_3V3']
                Voltage5v = ['14: Controller A', '0966: DISTR.VOLT_5V']
                Current5v = ['14: Controller A', '0976: DISTR.CURR_5V']
                VoltageBattery = ['14: Controller A', '0986: DISTR.VOLT_VBAT']
                CurrentBattery = ['14: Controller A', '0996: DISTR.CURR_VBAT']
                LCLState = ['14: Controller A', '1006: DISTR.LCL_STATE']
                LCLFlagB = ['14: Controller A', '1013: DISTR.LCL_FLAGS']

            class BatteryControler(object):
                Voltage = ['14: Controller A', '1019: BATC.VOLT_A']
                CurrentCharge = ['14: Controller A', '1029: BATC.CHRG_CURR']
                CurrentDischarge = ['14: Controller A', '1039: BATC.DCHRG_CURR']
                Temperature = ['14: Controller A', '1049: BATC.Temperature']
                State = ['14: Controller A', '1059: BATC.State']

            class BatteryPack(object):
                TemperatureA = ['14: Controller A', '1062: BP.Temperature A']
                TemperatureB = ['14: Controller A', '1075: BP.Temperature B']

            class Temperature(object):
                3v3 = ['14: Controller A', '1174: DCDC3V3.Temperature']
                5v = ['14: Controller A', '1184: DCDC5V.Temperature']
                MCU = ['14: Controller A', '1144: Temperature']
                Supply = ['14: Controller A', '1154: SUPP_TEMP']

            Safety_Counter = ['14: Controller A', '1088: Safety Counter']
            Power_Cycle_Count = ['14: Controller A', '1096: Power Cycle Count']
            Uptime = ['14: Controller A', '1112: Uptime']

            ControllerB_3V3d = ['14: Controller A', '1164: ControllerB.3V3d`']

        class B(object):
            BatteryPackTemperature = ['15: Controller B', '1194: BP.Temperature']

            class BatteryController(object):
                VOLT_B = ['15: Controller B', '1204: BATC.VOLT_B']

            Safety_Counter = ['15: Controller B', '1214: Safety Counter']
            Power_Cycle_Count = ['15: Controller B', '1222: Power Cycle Count']
            Uptime = ['15: Controller B', '1238: Uptime']

            ControllerA_3V3d = ['15: Controller B', '1290: ControllerA.3V3d']

            class Temperature(object):
                MCU = ['15: Controller B', '1270: Temperature']
                Supply = ['15: Controller B', '1280: SUPP_TEMP']

    class IMTQ(object):
        class Magnetometer(object):
            X = ['16: Imtq Magnetometers', '1300: Magnetometer Measurement 1']
            Y = ['16: Imtq Magnetometers', '1332: Magnetometer Measurement 2']
            Z = ['16: Imtq Magnetometers', '1364: Magnetometer Measurement 3']

        CoilActive = ['17: Imtq Coils Active', '1396: Coils active during measurement']

        class Dipole(object):
            X = ['18: Imtq Dipole', '1397: Dipole 1']
            Y = ['18: Imtq Dipole', '1413: Dipole 2']
            Z = ['18: Imtq Dipole', '1429: Dipole 3']

        class Bdot(object):
            X = ['18: Imtq Dipole', '1445: BDot 1']
            Y = ['18: Imtq Dipole', '1477: BDot 2']
            Z = ['18: Imtq Dipole', '1509: BDot 3']

        class Voltage(object):
            Digital = ['20: Imtq Housekeeping', '1541: Digital Voltage']
            Analog = ['20: Imtq Housekeeping', '1557: Analog Voltage']

        class Current(object):
            Digital = ['20: Imtq Housekeeping', '1573: Digital Current']
            Analog = ['20: Imtq Housekeeping', '1589: Analog Current']

        class Temperature(object):
            MCU = ['20: Imtq Housekeeping', '1605: MCU Temperature']
            class Coil(object):
                X = ['22: Imtq Temperature', '1669: Coil Temperature 1']
                Y = ['22: Imtq Temperature', '1685: Coil Temperature 2']
                Z = ['22: Imtq Temperature', '1701: Coil Temperature 3']

        class Current(object):
            class Coil(object):
                X = ['21: Imtq Coils', '1621: Coil Current 1']
                Y = ['21: Imtq Coils', '1637: Coil Current 2']
                Z = ['21: Imtq Coils', '1653: Coil Current 3']

        class State(object):
            Status = ['23: Imtq State', '1717: Status']
            Mode = ['23: Imtq State', '1725: Mode']
            ErrorDuringLastIteration = ['23: Imtq State', '1727: Error during previous iteration']
            ConfigurationChanged = ['23: Imtq State', '1735: Configuration changed']
            Uptime = ['23: Imtq State', '1736: Uptime']

        class SelfTest(object):
            class Error(object):
                INIT = ['24: Imtq Self Test', '1768: Error 1']
                X_PLUS = ['24: Imtq Self Test', '1776: Error 2']
                X_MINUS = ['24: Imtq Self Test', '1784: Error 3']
                Y_PLUS = ['24: Imtq Self Test', '1792: Error 4']
                Y_MINUS = ['24: Imtq Self Test', '1800: Error 5']
                Z_PLUS = ['24: Imtq Self Test', '1808: Error 6']
                Z_MINUS = ['24: Imtq Self Test', '1816: Error 7']
                FINA = ['24: Imtq Self Test', '1824: Error 8']


    def __init__(self, tmtc):
        self.tmtc = tmtc

        self.assert_equal = self.tm_check_decorator(nose.tools.assert_equal)
        self.assert_not_equal = self.tm_check_decorator(nose.tools.assert_not_equal)
        self.assert_true = self.tm_check_decorator(nose.tools.assert_true)
        self.assert_false = self.tm_check_decorator(nose.tools.assert_false)
        self.assert_is = self.tm_check_decorator(nose.tools.assert_is)
        self.assert_is_not = self.tm_check_decorator(nose.tools.assert_is_not)
        self.assert_is_none = self.tm_check_decorator(nose.tools.assert_is_none)
        self.assert_is_not_none = self.tm_check_decorator(nose.tools.assert_is_not_none)
        self.assert_in = self.tm_check_decorator(nose.tools.assert_in)
        self.assert_not_in = self.tm_check_decorator(nose.tools.assert_not_in)
        self.assert_is_instance = self.tm_check_decorator(nose.tools.assert_is_instance)
        self.assert_not_is_instance = self.tm_check_decorator(nose.tools.assert_not_is_instance)
        self.assert_raises = self.tm_check_decorator(nose.tools.assert_raises)
        self.assert_raises_regexp = self.tm_check_decorator(nose.tools.assert_raises_regexp)
        self.assert_almost_equal = self.tm_check_decorator(nose.tools.assert_almost_equal)
        self.assert_not_almost_equal = self.tm_check_decorator(nose.tools.assert_not_almost_equal)
        self.assert_greater = self.tm_check_decorator(nose.tools.assert_greater)
        self.assert_greater_equal = self.tm_check_decorator(nose.tools.assert_greater_equal)
        self.assert_less = self.tm_check_decorator(nose.tools.assert_less)
        self.assert_less_equal = self.tm_check_decorator(nose.tools.assert_less_equal)
        self.assert_regexp_matches = self.tm_check_decorator(nose.tools.assert_regexp_matches)
        self.assert_not_regexp_matches = self.tm_check_decorator(nose.tools.assert_not_regexp_matches)
        self.assert_items_equal = self.tm_check_decorator(nose.tools.assert_items_equal)
        self.assert_dict_contains_subset = self.tm_check_decorator(nose.tools.assert_dict_contains_subset)
        self.assert_multi_line_equal = self.tm_check_decorator(nose.tools.assert_multi_line_equal)
        self.assert_sequence_equal = self.tm_check_decorator(nose.tools.assert_sequence_equal)
        self.assert_list_equal = self.tm_check_decorator(nose.tools.assert_list_equal)
        self.assert_tuple_equal = self.tm_check_decorator(nose.tools.assert_tuple_equal)
        self.assert_set_equal = self.tm_check_decorator(nose.tools.assert_set_equal)
        self.assert_dict_equal = self.tm_check_decorator(nose.tools.assert_dict_equal)

        self.assert_equals = self.assert_equal
        self.assert_not_equals = self.assert_not_equal
        self.assert_almost_equals = self.assert_almost_equal
        self.assert_not_almost_equals = self.assert_not_almost_equal

    def get(self, name):
        value_actual = self.tmtc.beacon_value(name)
        PrintLog("{}: {}".format(name, value_actual))

    def tm_check_decorator(self, f):
        def wrapper(name, *args, **kwargs):
            frame = inspect.currentframe()
            try:
                context = inspect.getframeinfo(frame.f_back).code_context
                caller_lines = ''.join([line.strip() for line in context])
                PrintLog(caller_lines, ":", str(args), ",", str(kwargs))
            finally:
                del frame

            timeout = kwargs.pop('timeout', 0)
            timeout += 50  # OBC update 30 second + 10 second TX interval + 5 second RX
            while timeout > 0:
                try:
                    value_actual = self.tmtc.beacon_value(name)
                    f(value_actual, *args)
                    break
                except AssertionError:
                    # print "Retry"
                    time.sleep(1)
                    timeout -= 1
                    if timeout == 0:
                        PrintLog("Timeout expired!")
                        raise
        return wrapper
