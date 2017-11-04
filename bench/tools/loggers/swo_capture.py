import subprocess
import time
from multiprocessing import Process

from bench.tools.tools import SimpleLogger


class JlinkSWOLogger(object):
    def __init__(self, filename):
        self.logger = SimpleLogger(filename)
        self.thread = Process(target=self._run)

    def _run(self):
        print "Start!"
        process = subprocess.Popen('JLinkSWOViewer -device EFM32GG280F1024 -itmmask 0x1FFFF', shell=True,
                                        stdout=subprocess.PIPE, universal_newlines=True)
        while True:
            line = process.stdout.readline()
            self.logger.log(line)
            print line

    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.terminate()

if __name__ == "__main__":
    swo = JlinkSWOLogger('swo-output.log')
    swo.start()
    time.sleep(5)
    swo.stop()
