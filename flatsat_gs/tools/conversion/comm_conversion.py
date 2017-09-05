import math

class CommFormulas:
    @staticmethod
    def transparent_conversion(x):
        return x

    @staticmethod
    def vcc(x):
        return x*0.00488

    @staticmethod
    def tx_current(x):
        return x*0.0897

    @staticmethod
    def rx_current(x):
        return x*0.0305
    
    @staticmethod
    def doppler(x):
        return x*13.352 - 22300

    @staticmethod
    def signal_strength(x):
        return x*0.03 - 152

    @staticmethod
    def rf_power(x):
        return 20*math.log(x*0.00767, 10)

    @staticmethod
    def temperature(x):
        return x*(-0.0546) + 189.5522

comm_formulas = {'0602: Transmitter Current': CommFormulas.tx_current,
                '0614: Receiver Current': CommFormulas.rx_current,
                '0626: Doppler Offset': CommFormulas.doppler,
                '0638: Vcc': CommFormulas.vcc,
                '0650: Oscillator Temperature': CommFormulas.temperature,
                '0662: Receiver Amplifier Temperature': CommFormulas.temperature,
                '0674: Signal Strength': CommFormulas.signal_strength,
                '0686: RF Reflected Power': CommFormulas.rf_power,
                '0698: RF Forward Power': CommFormulas.rf_power,
                '0710: Transmitter Amplifier Temperature': CommFormulas.temperature,
                '0722: Transmitter Uptime Seconds': CommFormulas.transparent_conversion,
                '0728: Transmitter Uptime Minutes': CommFormulas.transparent_conversion,
                '0734: Transmitter Uptime Hours': CommFormulas.transparent_conversion,
                '0739: Transmitter Uptime Days': CommFormulas.transparent_conversion,
                '0747: Transmitter Idle State': CommFormulas.transparent_conversion,
                '0748: Beacon State': CommFormulas.transparent_conversion}
