import uplink
import thread
from threading import Timer
import aprs
import kiss
import time
import socket

class UDPKISS(kiss.KISS):

    """KISS TCP Class."""

    def __init__(self, host, port, strip_df_start=False):
        self.address = (host, int(port))
        self.strip_df_start = strip_df_start
        super(UDPKISS, self).__init__(strip_df_start)

    def _read_handler(self, read_bytes=None):
        read_bytes = read_bytes or kiss.READ_BYTES
        read_data = self.interface.recv(read_bytes)
        self._logger.debug('len(read_data)=%s', len(read_data))
        if read_data == '':
            raise kiss.SocketClosetError('Socket Closed')
        return read_data

    def stop(self):
        if self.interface:
            self.interface.shutdown(socket.SHUT_RDWR)

    def start(self):
        """
        Initializes the KISS device and commits configuration.
        """
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._logger.debug('Conntecting to %s', self.address)
        self.interface.connect(self.address)
        self._write_handler = self.interface.send

class Uplink:
    def __init__(self, host='localhost', port=8001):
        self.kiss = UDPKISS(host, port)
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
