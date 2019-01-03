import os

class GpredictTleLoader():
    def __init__(self, path):
        self._path = path

    def loadTle(self, noradId):
        tlePath = os.path.join(self._path, str(noradId) + ".sat")
        tleLines = []

        with open(tlePath, "r") as tleFile:
            for line in tleFile:
                if line.startswith("NAME="):
                    tleLines.append("0 {}".format(self._extractTleFromLine(line)))
                if "TLE" not in line:
                    continue
                tleLines.append(self._extractTleFromLine(line))

        return tleLines
                
    def _extractTleFromLine(self, line):
        return line.split("=")[1].strip()
