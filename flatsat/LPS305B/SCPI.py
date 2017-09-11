from serial import Serial


class SCPI(object):
    def __init__(self, com, baud=9600):
        self.hook = Serial(com, baud, timeout=5)

    def close(self):
        self.hook.close()

    def send(self, cmd):
        self.hook.write(cmd + '\r\n')

    def read(self):
        return self.hook.readline()

    def get_idn(self):
        self.send("*IDN?")
        return self.read()

    def reset(self):
        self.send("*RST?")

    def set_remote(self):
        self.send("SYST:REM")
