from serial import Serial
import io

import tools


class UARTLogger(object):
    def __init__(self, port, baudrate, filename, eol='\n'):
        self.logger = tools.SimpleLogger(filename)
        self.serial = Serial(port=port, baudrate=baudrate)

        self.ser_io = io.TextIOWrapper(io.BufferedRWPair(self.serial, self.serial, 1),
                                       newline=eol,
                                       line_buffering=True)

    def run(self):
        while True:
            line = self.ser_io.readline()
            self.logger.log(line)

if __name__ == "__main__":
    swo = UARTLogger('/dev/ttyACM2', 9600, 'uart-output.log')
    swo.run()
