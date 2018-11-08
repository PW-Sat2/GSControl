class Resources:
    def __init__(self, session, scheduled):
        self.session = session
        self.scheduled = scheduled

    @classmethod
    def init_with_zeros(self):
        session = Session(Downlink(0, Duration(0)),
                          Uplink(0, Duration(0)),
                          PowerBudget(Energy(0), MeanPower(0)))
        scheduled = Scheduled(Downlink(0, Durations([0, 0, 0, 0])),
                              PowerBudget(Energys([0, 0, 0, 0]), MeanPowers([0, 0, 0, 0])),
                              Duration(0),
                              Storage(0))
        return Resources(session, scheduled)

    @classmethod
    def session_names(self):
        return ['Session\ndownlink\nframes count',
                'Session\ndownlink\nduration [s]',
                'Session\nuplink\nframes count',
                'Session\nuplink\nduration [s]',
                'Session\npower\nbudget\nenergy [mWh]',
                'Session\npower\nbudget\nmean power [mW]']
        
    @classmethod
    def scheduled_names(self):
        return ['Scheduled\ndownlink\nframes\ncount',
                'Scheduled downlink\ndurations\n1200 2400 4800 9600\n[s]',
                'Scheduled power\nbudget energy\n1200 2400 4800 9600\n[mWh]',
                'Scheduled power\nbudget mean power\n1200 2400 4800 9600\n[mW]',
                'Scheduled\ntask\nduration\n[s]',
                'Scheduled\nstorage\nusage\n[kB]']

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
                str(resources.scheduled.task_duration),
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
                 task_duration,
                 storage):
        self.downlink = downlink
        self.power_budget = power_budget
        self.task_duration = task_duration
        self.storage = storage

    def __add__(self, other):
        return Scheduled(self.downlink + other.downlink,
                         self.power_budget + other.power_budget,
                         self.task_duration + other.task_duration,
                         self.storage + other.storage)


class Downlink:
    def __init__(self, frames_count, duration):
        self.frames_count = frames_count
        self.duration = duration

    def __add__(self, other):
        return Downlink(self.frames_count + other.frames_count,
                        self.duration + other.duration)


class Uplink:
    def __init__(self, frames_count, duration):
        self.frames_count = frames_count
        self.duration = duration

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
        if self.duration == 0:
            return 'N/A'
        return '{}'.format(str(round(self.duration, self.STR_PRECISION)))

    def __float__(self):
        return self.duration


class Durations:
    STR_PRECISION = 0
    UNIT = '[s, s, s, s]'

    def __init__(self, durations):
        self.durations = durations
    
    def __add__(self, other):
        durations = []
        for i in range(0, len(self.durations)):
            durations.append(self.durations[i] + other.durations[i])
        return Durations(durations)

    def __str__(self):
        output_str = ""

        for i in range(0, len(self.durations)):
            if self.durations[i] == 0:
                output_str += ' N/A'
            else:
                output_str += ' '
                output_str += str(int(round(self.durations[i], self.STR_PRECISION)))
        return '{}'.format(output_str)


class PowerBudget:
    def __init__(self, energy, mean_power):
        self.energy = energy
        self.mean_power = mean_power
    
    def __add__(self, other):
        return PowerBudget(self.energy + other.energy,
                           self.mean_power + other.mean_power)


class Energy:
    STR_PRECISION = 1
    UNIT = 'mWh'

    def __init__(self, energy):
        self.energy = energy

    def __add__(self, other):
        return Energy(self.energy + other.energy)

    def __str__(self):
        if self.energy == 0:
            return 'N/A'
        return str(round(self.energy, self.STR_PRECISION))
    
    def __float__(self):
        return self.energy


class Energys:
    STR_PRECISION = 0
    UNIT = '[mWh, mWh, mWh, mWh]'

    def __init__(self, energys):
        self.energys = energys
    
    def __add__(self, other):
        energys = []
        for i in range(0, len(self.energys)):
            energys.append(self.energys[i] + other.energys[i])
        return Energys(energys)

    def __str__(self):
        output_str = ""

        for i in range(0, len(self.energys)):
            if self.energys[i] == 0:
                output_str += ' N/A'
            else:
                output_str += ' '
                output_str += str(int(round(self.energys[i], self.STR_PRECISION)))
        return '{}'.format(output_str)



class MeanPower:
    STR_PRECISION = 1
    UNIT = 'mW'

    def __init__(self, mean_power):
        self.mean_power = mean_power

    def __add__(self, other):
        return MeanPower(self.mean_power + other.mean_power)

    def __str__(self):
        if self.mean_power == 0:
            return 'N/A'
        return str(round(self.mean_power, self.STR_PRECISION))
    
    def __float__(self):
        return self.mean_power


class MeanPowers:
    STR_PRECISION = 0
    UNIT = '[mW, mW, mW, mW]'

    def __init__(self, mean_powers):
        self.mean_powers = mean_powers

    def __add__(self, other):
        mean_powers = []
        for i in range(0, len(self.mean_powers)):
            mean_powers.append(self.mean_powers[i] + other.mean_powers[i])
        return MeanPowers(mean_powers)

    def __str__(self):
        output_str = ""

        for i in range(0, len(self.mean_powers)):
            if self.mean_powers[i] == 0:
                output_str += ' N/A'
            else:
                output_str += ' '
                output_str += str(int(round(self.mean_powers[i], self.STR_PRECISION)))
        return '{}'.format(output_str)


class Storage:
    STR_PRECISION = 1
    UNIT = 'kB'

    def __init__(self, storage_usage):
        self.storage_usage = storage_usage

    def __add__(self, other):
        return Storage(self.storage_usage + other.storage_usage)

    def __str__(self):
        if self.storage_usage == 0:
            return 'N/A'
        return str(round(self.storage_usage, self.STR_PRECISION))
