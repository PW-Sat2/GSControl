import os
import time

import saleae


class SaleaeLogger(object):
    def __init__(self):
        self.saleae = saleae.Saleae()

    def run(self, seconds=24 * 3600 * 30):
        self.saleae.set_capture_seconds(seconds)
        self.saleae.capture_start()

    def save(self, file):
        self.saleae.capture_stop()
        self.saleae.save_to_file(os.path.abspath(file))

if __name__ == "__main__":
    swo = SaleaeLogger()
    print "-------------- RUN 1 -------------"
    swo.run()
    time.sleep(10)

    swo.save('file1.logicdata')
