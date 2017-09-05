import math

class McuFormulas:
    @staticmethod
    def temperature(x):
        return x*(-0.0546) + 189.5522


mcu_formulas = {'Temperature': McuFormulas.temperature}
