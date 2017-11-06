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
