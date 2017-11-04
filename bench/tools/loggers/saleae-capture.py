import os
import time

import saleae


class SaleaeLogger(object):
    def __init__(self, filename):
        self.saleae = saleae.Saleae()
        self.file = filename

    def start(self):
        self.saleae.set_capture_seconds(24 * 3600 * 300)
        self.saleae.capture_start()

    def stop(self):
        self.saleae.capture_stop()
        self.saleae.save_to_file(os.path.abspath(self.file))

if __name__ == "__main__":
    swo = SaleaeLogger('file1.logicdata')
    swo.start()
    time.sleep(10)
    swo.stop()
