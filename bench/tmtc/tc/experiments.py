import telecommand.experiments as experiment
from response_frames.common import ExperimentSuccessFrame


class AbortExperiment(object):
    @staticmethod
    def send(tmtc):
        return tmtc.send_tc_with_response(experiment.AbortExperiment, ExperimentSuccessFrame)


class PerformSADSExperiment(object):
    @staticmethod
    def send(tmtc):
        return tmtc.send_tc_with_response(experiment.PerformSADSExperiment, ExperimentSuccessFrame)


class PerformSunSExperiment(object):
    def __init__(self, gain, itime, samples_count, short_delay, session_count, long_delay, filename):
        self.gain = gain
        self.itime = itime
        self.samples_count = samples_count
        self.short_delay = short_delay
        self.session_count = session_count
        self.long_delay = long_delay
        self.filename = filename

    def send(self, tmtc):
        return tmtc.send_tc_with_response(experiment.PerformSunSExperiment,
                                          ExperimentSuccessFrame,
                                          self.gain,
                                          self.itime,
                                          self.samples_count,
                                          self.short_delay,
                                          self.short_delay,
                                          self.session_count,
                                          self.long_delay,
                                          self.filename)


class PerformRadFETExperiment(object):
    def __init__(self, delay, samples_count, filename):
        self.delay = delay
        self.samples_count = samples_count
        self.filename = filename

    def send(self, tmtc):
        return tmtc.send_tc_with_response(experiment.PerformRadFETExperiment,
                                          ExperimentSuccessFrame,
                                          self.delay,
                                          self.samples_count,
                                          self.filename)


class PerformSailExperiment(object):
    @staticmethod
    def send(tmtc):
        return tmtc.send_tc_with_response(experiment.PerformSailExperiment, ExperimentSuccessFrame)


class PerformCameraCommissioningExperiment(object):
    @staticmethod
    def send(tmtc):
        return tmtc.send_tc_with_response(experiment.PerformCameraCommissioningExperiment, ExperimentSuccessFrame)


class PerformPayloadCommisioningExperiment(object):
    @staticmethod
    def send(tmtc):
        return tmtc.send_tc_with_response(experiment.PerformPayloadCommissioningExperiment, ExperimentSuccessFrame)
