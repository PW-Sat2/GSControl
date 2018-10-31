class Resources:
    def __init__(self, session, scheduled):
        self.session = session
        self.scheduled = scheduled

    @classmethod
    def init_with_zeros(self):
        session = Session(Downlink(0, Duration(0)),
                          Uplink(0, Duration(0)),
                          PowerBudget(0, 0))
        scheduled = Scheduled(Downlink(0, Duration(0)), 
                              PowerBudget(0, 0), 
                              Storage(0))
        return Resources(session, scheduled)

    @classmethod
    def session_names(self):
        return ['Session downlink frames count',
                'Session downlink duration [s]',
                'Session uplink frames count',
                'Session uplink duration [s]',
                'Session power budget energy [mWh]',
                'Session power budget mean power [mW]']
        
    @classmethod
    def scheduled_names(self):
        return ['Scheduled downlink frames count',
                'Scheduled downlink duration [s]',
                'Scheduled power budget energy [mWh]',
                'Scheduled power budget mean power [mW]',
                'Scheduled storage usage [kB]']

    @classmethod
    def session_params(self, resources):
        return [str(resources.session.downlink.frames_count),
                str(resources.session.downlink.duration),
                str(resources.session.uplink.frames_count),
                str(resources.session.uplink.duration),
                str(resources.session.power_budget.energy),
                str(resources.session.power_budget.mean_power)]
    
    @classmethod
    def scheduled_params(self, resources):
        return [str(resources.scheduled.downlink.frames_count),
                str(resources.scheduled.downlink.duration),
                str(resources.scheduled.power_budget.energy),
                str(resources.scheduled.power_budget.mean_power),
                str(resources.scheduled.storage)]

    def __add__(self, other):
        return Resources(self.session + other.session,
                         self.scheduled + other.scheduled)


class Session:
    def __init__(self, 
                 downlink,
                 uplink,
                 power_budget):
        self.uplink = uplink
        self.downlink = downlink
        self.power_budget = power_budget


    def __add__(self, other):
        return Session(self.downlink + other.downlink,
                       self.uplink + other.uplink,
                       self.power_budget + other.power_budget)


class Scheduled:
    def __init__(self,
                 downlink,
                 power_budget,
                 storage):
        self.downlink = downlink
        self.power_budget = power_budget
        self.storage = storage

    def __add__(self, other):
        return Scheduled(self.downlink + other.downlink,
                         self.power_budget + other.power_budget,
                         self.storage + other.storage)


class Downlink:
    def __init__(self, frames_count, duration):
        self.frames_count = frames_count
        self.duration = duration

    def init_with_zeros(self):
        return Downlink(0, 0)

    def __add__(self, other):
        return Downlink(self.frames_count + other.frames_count,
                        self.duration + other.duration)


class Uplink:
    def __init__(self, frames_count, duration):
        self.frames_count = frames_count
        self.duration = duration

    def init_with_zeros(self):
        return Uplink(0, 0)
    
    def __add__(self, other):
        return Uplink(self.frames_count + other.frames_count,
                      self.duration + other.duration)


class Duration:
    STR_PRECISION = 2
    UNIT = 's'

    def __init__(self, duration):
        self.duration = duration

    def __add__(self, other):
        return Duration(self.duration + other.duration)

    def __str__(self):
        return '{}'.format(str(round(self.duration, self.STR_PRECISION)))

    def __float__(self):
        return round(self.duration, self.STR_PRECISION)


class PowerBudget:
    def __init__(self, energy, mean_power):
        self.energy = energy
        self.mean_power = mean_power
    
    def __add__(self, other):
        return PowerBudget(self.energy + other.energy,
                           self.mean_power + other.mean_power)


class Energy:
    STR_PRECISION = 0
    UNIT = 'mWh'

    def __init__(self, energy):
        self.energy_mWh = energy

    def energy(self):
        return round(self.energy_mWh, self.STR_PRECISION)

    def __add__(self, other):
        return Energy(self.energy_mWh + other.energy())

    def __str__(self):
        return str(round(self.energy_mWh, self.STR_PRECISION))


class MeanPower:
    STR_PRECISION = 0
    UNIT = 'mW'

    def __init__(self, mean_power):
        self.mean_power_mW = mean_power

    def mean_power(self):
        return round(self.mean_power_mW, self.STR_PRECISION)

    def __add__(self, other):
        return MeanPower(self.mean_power_mW + other.mean_power())

    def __str__(self):
        return str(round(self.mean_power_mW, self.STR_PRECISION))


class Storage:
    STR_PRECISION = 0
    UNIT = 'kB'

    def __init__(self, storage_usage):
        self.storage_usage_kB = storage_usage

    def storage_usage(self):
        return round(self.storage_usage_kB, self.STR_PRECISION)

    def __add__(self, other):
        return Storage(self.storage_usage_kB + other.storage_usage_kB)

    def __str__(self):
        return str(round(self.storage_usage_kB, self.STR_PRECISION))
