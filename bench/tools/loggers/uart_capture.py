import io
from multiprocessing import Process
from time import sleep

import bench.tools.tools
from serial import Serial


class UARTLogger(object):
    def __init__(self, port, baudrate, filename, eol='\n'):
        self.logger = bench.tools.tools.SimpleLogger(filename)
        self.serial = Serial(port=port, baudrate=baudrate)

        self.ser_io = io.TextIOWrapper(io.BufferedRWPair(self.serial, self.serial, 1),
                                       newline=eol,
                                       line_buffering=True)
        self.thread = Process(target=self._run)

    def _run(self):
        self.serial.flush()
        self.serial.flushInput()
        self.serial.flushOutput()
        while True:
            line = self.ser_io.readline()
            self.logger.log(line)

    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.terminate()

if __name__ == "__main__":
    uart = UARTLogger('/dev/ttyACM2', 9600, 'uart-output.log')
    uart.start()
    sleep(5)
    uart.stop()
