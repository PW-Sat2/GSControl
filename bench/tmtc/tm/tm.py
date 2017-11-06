import time
import inspect
import nose.tools

from tools.tools import PrintLog


class TM(object):
    class COMM(object):
        class TX(object):
            IdleState = ['11: Comm', '0665: Transmitter Idle State']

    class Experiments(object):
        CurrentExperimentCode = ['09: Experiments', '0490: Current experiment code']
        CurrentExperimentStartupResult = ['09: Experiments', '0494: Experiment Startup Result']
        LastExperimentIterationStatus = ['09: Experiments', '0502: Last Experiment Iteration Status']

    class EPS(object):
        class ControllerA(object):
            class MPPT(object):
                class X(object):
                    SOL_VOLT = ['14: Controller A', '0793: MPPT_X.SOL_VOLT']
                    SOL_CURR = ['14: Controller A', '0805: MPPT_X.SOL_CURR']
                    SOL_OUT_VOLT = ['14: Controller A', '0817: MPPT_X.SOL_OUT_VOLT']
                    Temperature = ['14: Controller A', '0829: MPPT_X.Temperature']
                    State = ['14: Controller A', '0841: MPPT_X.State']

                class Y_Plus(object):
                    SOL_VOLT = ['14: Controller A', '0844: MPPT_Y+.SOL_VOLT']
                    SOL_CURR = ['14: Controller A', '0856: MPPT_Y+.SOL_CURR']
                    SOL_OUT_VOLT = ['14: Controller A', '0868: MPPT_Y+.SOL_OUT_VOLT']
                    Temperature = ['14: Controller A', '0880: MPPT_Y+.Temperature']
                    State = ['14: Controller A', '0892: MPPT_Y+.State']

                class Y_Minus(object):
                    SOL_VOLT = ['14: Controller A', '0895: MPPT_Y-.SOL_VOLT']
                    SOL_CURR = ['14: Controller A', '0907: MPPT_Y-.SOL_CURR']
                    SOL_OUT_VOLT = ['14: Controller A', '0919: MPPT_Y-.SOL_OUT_VOLT']
                    Temperature = ['14: Controller A', '0931: MPPT_Y-.Temperature']
                    State = ['14: Controller A', '0943: MPPT_Y-.State']

            class Distribution(object):
                VOLT_3V3 = ['14: Controller A', '0946: DISTR.VOLT_3V3']
                CURR_3V3 = ['14: Controller A', '0956: DISTR.CURR_3V3']
                VOLT_5V = ['14: Controller A', '0966: DISTR.VOLT_5V']
                CURR_5V = ['14: Controller A', '0976: DISTR.CURR_5V']
                VOLT_VBAT = ['14: Controller A', '0986: DISTR.VOLT_VBAT']
                CURR_VBAT = ['14: Controller A', '0996: DISTR.CURR_VBAT']
                LCL_STATE = ['14: Controller A', '1006: DISTR.LCL_STATE']
                LCL_FLAGS = ['14: Controller A', '1013: DISTR.LCL_FLAGS']

            class BatteryControler(object):
                VOLT_A = ['14: Controller A', '1019: BATC.VOLT_A']
                CHRG_CURR = ['14: Controller A', '1029: BATC.CHRG_CURR']
                DCHRG_CURR = ['14: Controller A', '1039: BATC.DCHRG_CURR']
                Temperature = ['14: Controller A', '1049: BATC.Temperature']
                State = ['14: Controller A', '1059: BATC.State']

            class BatteryPack(object):
                Temperature_A = ['14: Controller A', '1062: BP.Temperature A']
                Temperature_B = ['14: Controller A', '1075: BP.Temperature B']

            class Temperature(object):
                DCDC3V3 = ['14: Controller A', '1174: DCDC3V3.Temperature']
                DCDC5V = ['14: Controller A', '1184: DCDC5V.Temperature']
                Mcu = ['14: Controller A', '1144: Temperature']
                Supply = ['14: Controller A', '1154: SUPP_TEMP']

            class System(object):
                Safety_Counter = ['14: Controller A', '1088: Safety Counter']
                Power_Cycle_Count = ['14: Controller A', '1096: Power Cycle Count']
                Uptime = ['14: Controller A', '1112: Uptime']

            class ControllerB(object):
                ControllerB_3V3d = ['14: Controller A', '1164: ControllerB.3V3d`']

        class ControllerB(object):
            class BatteryPack(object):
                Temperature = ['15: Controller B', '1194: BP.Temperature']

            class BatteryController(object):
                VOLT_B = ['15: Controller B', '1204: BATC.VOLT_B']

            class System(object):
                Safety_Counter = ['15: Controller B', '1214: Safety Counter']
                Power_Cycle_Count = ['15: Controller B', '1222: Power Cycle Count']
                Uptime = ['15: Controller B', '1238: Uptime']

            class ControllerA(object):
                ControllerA_3V3d = ['15: Controller B', '1290: ControllerA.3V3d']

            class Temperature(object):
                Mcu = ['15: Controller B', '1270: Temperature']
                Supply = ['15: Controller B', '1280: SUPP_TEMP']


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
