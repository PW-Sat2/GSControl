import nose.tools
import inspect

from tools import PrintLog


def my_decorator(f):
    def wrapper(*args, **kwargs):
        frame = inspect.currentframe()
        try:
            context = inspect.getframeinfo(frame.f_back).code_context
            caller_lines = ''.join([line.strip() for line in context])
            PrintLog(caller_lines, ":", str(args), ",", str(kwargs))
            return f(*args, **kwargs)
        finally:
            del frame
    return wrapper


assert_equal = my_decorator(nose.tools.assert_equal)
assert_not_equal = my_decorator(nose.tools.assert_not_equal)
assert_true = my_decorator(nose.tools.assert_true)
assert_false = my_decorator(nose.tools.assert_false)
assert_is = my_decorator(nose.tools.assert_is)
assert_is_not = my_decorator(nose.tools.assert_is_not)
assert_is_none = my_decorator(nose.tools.assert_is_none)
assert_is_not_none = my_decorator(nose.tools.assert_is_not_none)
assert_in = my_decorator(nose.tools.assert_in)
assert_not_in = my_decorator(nose.tools.assert_not_in)
assert_is_instance = my_decorator(nose.tools.assert_is_instance)
assert_not_is_instance = my_decorator(nose.tools.assert_not_is_instance)
assert_raises = my_decorator(nose.tools.assert_raises)
assert_raises_regexp = my_decorator(nose.tools.assert_raises_regexp)
assert_almost_equal = my_decorator(nose.tools.assert_almost_equal)
assert_not_almost_equal = my_decorator(nose.tools.assert_not_almost_equal)
assert_greater = my_decorator(nose.tools.assert_greater)
assert_greater_equal = my_decorator(nose.tools.assert_greater_equal)
assert_less = my_decorator(nose.tools.assert_less)
assert_less_equal = my_decorator(nose.tools.assert_less_equal)
assert_regexp_matches = my_decorator(nose.tools.assert_regexp_matches)
assert_not_regexp_matches = my_decorator(nose.tools.assert_not_regexp_matches)
assert_items_equal = my_decorator(nose.tools.assert_items_equal)
assert_dict_contains_subset = my_decorator(nose.tools.assert_dict_contains_subset)
assert_multi_line_equal = my_decorator(nose.tools.assert_multi_line_equal)
assert_sequence_equal = my_decorator(nose.tools.assert_sequence_equal)
assert_list_equal = my_decorator(nose.tools.assert_list_equal)
assert_tuple_equal = my_decorator(nose.tools.assert_tuple_equal)
assert_set_equal = my_decorator(nose.tools.assert_set_equal)
assert_dict_equal = my_decorator(nose.tools.assert_dict_equal)

assert_equals = assert_equal
assert_not_equals = assert_not_equal
assert_almost_equals = assert_almost_equal
assert_not_almost_equals = assert_not_almost_equal
