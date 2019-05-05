import json
import os

class CallsignDecoder:
    def __init__(self, callsign_file):
        self.personal_data = None
        self.blacklist = [
            "721762dd-8b8f-44b3-bfa7-66cfb12d39e1", # FP
            "e3fe087d-bf9c-4e4d-80c7-3366cfdec3e3", # Elka
        ]
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

    def is_on_black_list(self, userId):
        return userId in self.blacklist

