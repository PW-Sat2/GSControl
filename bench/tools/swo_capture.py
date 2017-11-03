import subprocess
import tools


class JlinkSWOLogger(object):
    def __init__(self, file):
        self.logger = tools.SimpleLogger(file)

    def run(self):
        process = subprocess.Popen('JLinkSWOViewer -device EFM32GG280F1024 -itmmask 0x1FFFF', shell=True, stdout=subprocess.PIPE, universal_newlines=True)

        while True:
            line = process.stdout.readline()
            self.logger.log(line)

if __name__ == "__main__":
    swo = JlinkSWOLogger('swo-output.log')
    swo.run()
