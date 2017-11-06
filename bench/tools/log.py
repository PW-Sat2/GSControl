import time
import os
import traceback

from config import config


class SimpleLogger:
    def __init__(self, filename, in_test=False, stdout=False):
        self.filename = filename
        self.in_test = in_test
        self.stdout = stdout

    @staticmethod
    def format(*text):
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
        with open(self._path(), 'a') as f:
            line = self.format(*text)
            f.writelines(line + '\n')
            if self.stdout:
                print line


_log_logger = SimpleLogger('log.log', in_test=True, stdout=True)
_main_logger = SimpleLogger('main.log', in_test=False, stdout=True)

PrintLog = _log_logger.log
MainLog = _main_logger.log
