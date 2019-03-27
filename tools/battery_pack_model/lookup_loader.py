import os


class FloatLookupLoader:
    def __init__(self, path):
        self.lookup = self.load_from_file(path)

    def load_from_file(self, path):
        with open(os.path.join(os.path.dirname(__file__)) + "/" + path, 'r') as file:
            file_content = file.read().split("\n")
            file.close()
            list = []
            for line in range(0, len(file_content)):
                list.append(file_content[line].split(","))
            return list
        return []

    def to_wh(self, bp_voltage):
        bp_voltage = round(bp_voltage, 2)

        if bp_voltage < 5.6:
            bp_voltage = 5.6
        if bp_voltage > 8.4:
            bp_voltage = 8.4

        return float(self.lookup[int((bp_voltage - 5.6) / 0.01) + 1][1])
