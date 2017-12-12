import telecommand.antenna
import response_frames.operation


class SetAntennaDeployment(object):
    def __init__(self, disabled=True):
        self.disabled = disabled

    def send(self, tmtc):
        return tmtc.send_tc_with_response(telecommand.antenna.SetAntennaDeployment,
                                          response_frames.operation.OperationSuccessFrame,
                                          self.disabled)
