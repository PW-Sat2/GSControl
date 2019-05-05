import json
import os

class CallsignDecoder:
    def __init__(self, callsign_file):
        self.personal_data = None
        if callsign_file and os.path.exists(callsign_file):
            try:
                with open(callsign_file, "r") as infile:
                    self.personal_data = json.load(infile)
            except Exception:
                pass

    def decode(self, userId):
        if not self.personal_data:
            return None

        try:
            return self.personal_data[userId]['callsign']
        except Exception:
            return "???"

