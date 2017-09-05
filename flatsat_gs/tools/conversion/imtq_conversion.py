import math

class ImtqFormulas:
    @staticmethod
    def magnetometer(x):
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


comm_formulas = {'Beacon State': CommFormulas.transparent_conversion,
          'Doppler Offset': CommFormulas.doppler,
          'Oscillator Temperature': CommFormulas.temperature,
          'RF Forward Power': CommFormulas.rf_power,
          'RF Reflected Power': CommFormulas.rf_power,
          'Receiver Amplifier Temperature': CommFormulas.temperature,
          'Receiver Current': CommFormulas.rx_current,
          'Signal Strength': CommFormulas.signal_strength,
          'Transmitter Amplifier Temperature': CommFormulas.temperature,
          'Transmitter Current': CommFormulas.tx_current,
          'Transmitter Idle State': CommFormulas.transparent_conversion,
          'Transmitter Uptime Days': CommFormulas.transparent_conversion,
          'Transmitter Uptime Hours': CommFormulas.transparent_conversion,
          'Transmitter Uptime Minutes': CommFormulas.transparent_conversion,
          'Transmitter Uptime Seconds': CommFormulas.transparent_conversion,
          'Vcc': CommFormulas.vcc}
