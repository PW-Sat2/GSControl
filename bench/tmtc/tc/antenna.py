import telecommand.antenna
import response_frames.operation


class StopAntennaDeployment(object):
    def send(self, tmtc):
        return tmtc.send_tc_with_response(telecommand.antenna.StopAntennaDeployment, response_frames.operation.OperationSuccessFrame)
