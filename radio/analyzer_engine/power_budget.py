class Orbit:
    DURATION = 98.8 * 60

class Check:

    @classmethod
    def in_range(self, value, low, high):
        try:
            len(value)

            output_values = []
            for index in range(0, len(value)):
                output_values.append(self.in_range(value[index], low, high))
            return output_values
        except TypeError:
            pass

        if value >= low and value <= high:
            return True
        return False


class CommTransmitter:
    TX_PREAMBLE_TIME = 0.3
    TX_PEAK_PWR = 3.0

    def __init__(self):
        pass

    @classmethod
    def total_tx_time(self, message_length, bitrate):
        return ((message_length * 8) / bitrate) + self.TX_PREAMBLE_TIME

    @classmethod
    def periodic_mean_power(self,
                            message_length,
                            interval_minutes,
                            bitrate=1200,
                            repeat_count=1):
        if not Check.in_range(value=interval_minutes, low=1, high=255):
            raise ValueError('Interval in minutes out of range')

        tx_time = self.total_tx_time(message_length, bitrate) * repeat_count
        return (tx_time / (interval_minutes * 60.0)) * self.TX_PEAK_PWR

    @classmethod
    def idle_state_energy(self, duration):
        return (duration / 3600.0) * self.TX_PEAK_PWR


class CommReceiver:
    RX_MEAN_POWER = 0.51

    def __init__(self):
        pass

    @classmethod
    def mean_power_consumption(self):
        return self.RX_MEAN_POWER

    @classmethod
    def energy_consumption_per_orbit(self):
        return (Orbit.DURATION / 3600.0) * self.RX_MEAN_POWER

