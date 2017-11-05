from tools import PrintLog


def check_equal(name, value1, value2):
    PrintLog("{}: {} == {}".format(name, value1, value2))
    assert(value1 == value2)