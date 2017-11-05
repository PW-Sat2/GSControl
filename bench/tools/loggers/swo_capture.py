import subprocess
import time
from multiprocessing import Process

from tools.tools import SimpleLogger, MainLog


class JlinkSWOLogger(object):
    def __init__(self):
        self.logger = SimpleLogger('swo.log')
        self.thread = Process(target=self._run)
        self.process = subprocess.Popen(['JLinkSWOViewer', '-device', 'EFM32GG280F1024', '-itmmask', '0x1FFFF'],
                                        stdout=subprocess.PIPE, universal_newlines=True)
        MainLog("Starting SWO logger".format())

    def _run(self):
        while True:
            line = self.process.stdout.readline()
            self.logger.log(line)

    def start(self):
        self.thread.start()

    def stop(self):
        self.process.terminate()
        self.thread.terminate()

if __name__ == "__main__":
    swo = JlinkSWOLogger()
    swo.start()
    time.sleep(5)
    swo.stop()
