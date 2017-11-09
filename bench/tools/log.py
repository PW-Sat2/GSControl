import time
import os
import csv
import io

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

    def _first_iteration(self, dict_to_write):
        self.format = self._get_header
        SimpleLogger.log(self, dict_to_write)  # print header
        return self._get_data(dict_to_write)   # print data

    def _get_header(self, dict_to_write):
        self.format = self._get_data
        # change to list of timestamp + all keys in dictionary
        return self._get_csv(["timestamp"] + dict_to_write.keys())

    def _get_data(self, dict_to_write):
        # change to list of timestamp + all values
        return self._get_csv([str(time.time())] + dict_to_write.values())

    @staticmethod
    def _get_csv(list_to_write):
        output = io.BytesIO()
        writer = csv.writer(output)
        writer.writerow(list_to_write)
        return output.getvalue()[:-1]  # remove newline (it will be added by SimpleLogger)
