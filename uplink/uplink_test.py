import uplink
import thread
from threading import Timer
import aprs
import kiss
import time

class Uplink:
    def __init__(self, host='localhost', port=8001):
        self.kiss = kiss.TCPKISS(host, port)
        self.frame = aprs.Frame()
        self.frame.source = self.frame.destination = aprs.Callsign("PWSAT2-0");
        self.frame.text = ""

    def start(self):
        self.kiss.start()

    def stop(self):
        self.kiss.stop()

    def send(self, payload):
        self.frame.text = payload
        self.kiss.write(self.frame.encode_kiss())


if __name__ == "__main__":
    up = Uplink()
    up.start()
    up.send("AAAAAAAAAAAAAAAA")
    up.send("BBBBBBBBBBBBBBBB")
    up.send("CCCCCCCCCCCCCCCC")

    time.sleep(5)

    up.stop()
