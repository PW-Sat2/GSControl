import telecommand.sail
from response_frames.stop_sail_deployment import StopSailDeploymentSuccessFrame
from response_frames.common import SailSuccessFrame


class OpenSailTelecommand(object):
    def __init__(self, ignore_overheat):
    	self.ignore_overheat = ignore_overheat

    def send(self, tmtc):
        tmtc.send_tc_with_response(telecommand.sail.OpenSailTelecommand, SailSuccessFrame, self.ignore_overheat)


class StopSailDeployment(object):
    @staticmethod
    def send(tmtc):
        tmtc.send_tc_with_response(telecommand.sail.StopSailDeployment, StopSailDeploymentSuccessFrame)
