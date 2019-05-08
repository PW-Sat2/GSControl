import time
import os
import sys
import websocket
import traceback

class Receiver(object):
    def __init__(self, target="wss://radio.pw-sat.pl/communication/log/ws", origin="https://radio.pw-sat.pl/"):
        self.target = target
        self.origin = origin
        self.ws = None
        self.open_ws()

    def open_ws(self):
        self.ws = websocket.WebSocketApp(url=self.target,
                            on_open = self._on_open,
                            on_message = self._on_message,
                            on_error = self._on_error,
                            on_close = self._on_close,
                            )

    def run_forever(self):
        self.ws.run_forever(origin=self.origin, ping_interval=30)

    def shutdown(self):
        self.ws.close()

    def enable_debug(self):
        websocket.enableTrace(True)

    def _on_open(self):
        print("Initializing connection.")

    def _on_message(self, data):
        print(data)

    def _on_error(self, error):
        print(error)

    def _on_close(self):
        print("Connection closed.")
