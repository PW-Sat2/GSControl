from SCPI import SCPI
import time


class LS305B(SCPI):
    class Channel:
        CH1 = "CH1"
        CH2 = "CH2"
        CH3 = "CH3"

    def __init__(self, com):
        super(LS305B, self).__init__(com)

        resp = self.get_idn()
        if resp.__contains__("BK, LPS305B-TC"):
            bk_serial_number = resp.split(', ')
            print "New BK LPS305B-TC detected. Serial number: " + bk_serial_number[2] + ". Connected!"
        
            self.set_remote()
            self.set_output_to_zero()
            self.disable_output()
        else:
            print "Bad response from BK LPS305B!: " + resp

    def enable_output(self):
        self.send("OUTP:STAT:ALL 1")

    def disable_output(self):
        self.send("OUTP:STAT:ALL 0")

    def set(self, channel, voltage, current):
        s = "APPL " + channel + ", " + str(int(1000*voltage)) + "mV, " + str(int(1000*current)) + "mA"
        self.send(s)

    def set_output_to_zero(self):
        self.set(self.Channel.CH1, 0, 0)
        self.set(self.Channel.CH2, 0, 0)
        self.set(self.Channel.CH3, 0, 0)
