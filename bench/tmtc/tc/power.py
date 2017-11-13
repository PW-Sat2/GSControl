import telecommand.power
import response_frames.operation


class PowerCycle(object):
    @staticmethod
    def send(tmtc):
        return tmtc.send_tc_with_response(telecommand.power.PowerCycleTelecommand, response_frames.operation.PowerSuccessFrame)
