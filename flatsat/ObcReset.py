import time
import serial

class ObcReset(object):
    def __init__(self, port):
        self.port = port

    def perform_reset(self):
        print("Performing OBC reset...")
        obcReset = serial.Serial(self.port, 9600)
        time.sleep(3)
        obcReset.setDTR(False)
        time.sleep(0.5)
        obcReset.setDTR(True)
        obcReset.close()

