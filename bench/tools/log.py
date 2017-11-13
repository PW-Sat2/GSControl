import time
import os
import csv
import io
from functools import reduce

from config import config


class SimpleLogger:
    def __init__(self, filename, in_test=False, stdout=False):
        self.filename = filename
        self.in_test = in_test
        self.stdout = stdout

    def format(self, *text):
        line = ' '.join([str(i) for i in text])
        line = line.strip()
        return '[' + time.strftime('%H:%M:%S') + '] ' + line

    def _path(self):
        path = config['output_path']

        if self.in_test:
            path = os.path.join(path, config['test_name'])

        path = os.path.join(path, self.filename)
        return path

    def log(self, *text):
        line = self.format(*text)
        with open(self._path(), 'a') as f:
            f.writelines(line + '\n')
            if self.stdout:
                print line


_log_logger = SimpleLogger('log.log', in_test=True, stdout=True)
_main_logger = SimpleLogger('main.log', in_test=False, stdout=True)

PrintLog = _log_logger.log
MainLog = _main_logger.log


class CSVLogger(SimpleLogger):
    def __init__(self, filename, in_test=False):
        SimpleLogger.__init__(self, filename, in_test)
        self.format = self._first_iteration

    def _first_iteration(self, *dicts):
        self.format = self._get_header
        SimpleLogger.log(self, *dicts)  # print header
        return self._get_data(*dicts)   # print data

    def _get_header(self, *dicts):
        self.format = self._get_data
        # change to list of timestamp + sorted keys for every passed dictionary
        all_keys = reduce(lambda x, y: x + y, [sorted(i.keys()) for i in dicts])
        return self._get_csv(["timestamp"] + all_keys)

    def _get_data(self, *dicts):
        # change to list of timestamp + all values
        all_values = reduce(lambda x, y: x + y, [[d[key] for key in sorted(d.keys())] for d in dicts])

        return self._get_csv([time.strftime('%H:%M:%S')] + all_values)

    @staticmethod
    def _get_csv(list_to_write):
        output = io.BytesIO()
        writer = csv.writer(output)
        writer.writerow(list_to_write)
        return output.getvalue()[:-1]  # remove newline (it will be added by SimpleLogger)
