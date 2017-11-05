import os
import time
from multiprocessing import Process

import saleae
from config import config
from tools.tools import MainLog


class SaleaeLogger(object):
    def __init__(self):
        self.saleae = saleae.Saleae()
        self.saleae.set_capture_seconds(24 * 3600 * 300)
        self.thread = Process(target=self._run)
        MainLog("Started Saleae")

    def _run(self):
        while True:
            MainLog("Saleae start record")
            self.saleae.capture_start()
            try:
                while not self.saleae.is_processing_complete():
                    time.sleep(1)
            except self.saleae.CommandNAKedError:
                MainLog("Saleae CommandNAKedError Exception!")
            MainLog("Saleae record failed!")
            self._save()

    def _save(self):
        name = 'saleae.logicdata'
        if os.path.isfile(os.path.join(config['output_path'], name)):
            suf = 1
            while os.path.isfile(os.path.join(config['output_path'], 'saleae_' + str(suf) + '.logicdata')):
                suf += 1
            name = 'saleae_' + str(suf) + '.logicdata'

        MainLog("Saleae saving to {}".format(name))
        self.saleae.save_to_file(os.path.join(config['output_path'], name))

    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.terminate()
        self.saleae.capture_stop()
        self._save()


if __name__ == "__main__":
    swo = SaleaeLogger()
    swo.start()
    time.sleep(10)
    swo.stop()
