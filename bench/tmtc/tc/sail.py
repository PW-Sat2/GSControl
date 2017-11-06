import telecommand.sail
from response_frames.stop_sail_deployment import StopSailDeploymentSuccessFrame


class StopSailDeployment(object):
    @staticmethod
    def send(tmtc):
        tmtc.send_tc_with_response(telecommand.sail.StopSailDeployment, StopSailDeploymentSuccessFrame)
