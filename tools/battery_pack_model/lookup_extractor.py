import os, sys

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

class RawLookup:
    def __init__(self, lookup, voltage_quant, ah_quant):
        self.lookup = lookup
        self.max = max(self.lookup)
        self.voltage_quant = voltage_quant
        self.ah_quant = ah_quant


class FloatLookupExporter:
    def __init__(self):
        self.raw_lookup = ImageToLookupConverter()

    def save_to_file(self, path):
        with open(os.path.join(os.path.dirname(__file__)) + "/" + path, 'w') as file:
            file.write("Voltage[V],Energy[Wh]\n")
            for voltage in np.arange(5.6, 8.4, 0.01):
                file.write(str(round(voltage,2)) + "," + str(round(self.raw_lookup.to_wh(voltage), 2)) + "\n")
            file.close()


class ImageToLookupConverter:
    BP_DCHRG_IMG = 'bp_discharge_20deg.png'

    def __init__(self):
        self.chart_x = []
        self.chart_y = []
        self.bp_discharge = self.generate_lookup(self.BP_DCHRG_IMG)

    def generate_lookup(self, chart_path):
        im = Image.open(os.path.join(os.path.dirname(__file__)) + "/" + chart_path)
        pix = im.load()

        for x in range(0, im.size[0]):
            for y in range(0, im.size[1]):
                if pix[x,y][0] == 0xff and \
                   pix[x,y][1] == 0x00 and \
                   pix[x,y][2] == 0x00:
                    self.chart_x.append(x)
                    self.chart_y.append(y)

        lookup = []
        for y in range(0, max(self.chart_y) + 1):
            lookup.append(None)

        for pixel in range(0, len(self.chart_y)):
            if lookup[self.chart_y[pixel]] == None:
                lookup[(self.chart_y[pixel] - min(self.chart_y))] = self.chart_x[pixel] - min(self.chart_x)

        voltage_quant = (4.2 - 2.8) / (max(self.chart_y) - min(self.chart_y))
        ah_quant = 2.588 / max(lookup)

        return RawLookup(lookup, voltage_quant, ah_quant)

    def to_lookup_index(self, cell_voltage):
        return ((max(self.chart_y) - min(self.chart_y))) - int(((cell_voltage - 2.8) / self.bp_discharge.voltage_quant))

    def to_ah(self, cell_voltage):
        return 2.588 - (self.bp_discharge.lookup[self.to_lookup_index(cell_voltage)] * self.bp_discharge.ah_quant)

    def to_wh(self, bp_voltage):
        return ((self.to_ah(bp_voltage / 2.0) * 2.0) * 3.7) * 2.0
