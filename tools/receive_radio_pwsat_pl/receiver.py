import time
import os
import sys
import websocket
import traceback

class Receiver:
    def __init__(self, target="wss://radio.pw-sat.pl/communication/log/ws", origin="https://radio.pw-sat.pl/"):
        self.target = target
        self.origin = origin
        self.ws = None
        self.open_ws()

    def open_ws(self):
        self.ws = websocket.create_connection(self.target, origin=self.origin)

    def get(self):
        return self.ws.recv()
