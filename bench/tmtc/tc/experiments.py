import telecommand.experiments as experiment
from response_frames.common import ExperimentSuccessFrame


class AbortExperiment(object):
    def send(self, tmtc):
        return tmtc.send_tc_with_response(experiment.SendBeacon(), ExperimentSuccessFrame)


class PerformSADSExperiment(object):
    def send(self, tmtc):
        return tmtc.send_tc_with_response(experiment.PerformSADSExperiment(), ExperimentSuccessFrame)
