import logging

from summary.scope import session


def load_telemetry_file(file_name):
    logging.info('Load telemetry file {}'.format(file_name))
