import telecommand.eps
import response_frames.disable_overheat_submode

class DisableOverheatSubmode(object):
    def __init__(self, controller):
    	self.controller = controller

    def send(self, tmtc):
        return tmtc.send_tc_with_response(telecommand.eps.DisableOverheatSubmode, response_frames.disable_overheat_submode.DisableOverheatSubmodeSuccessFrame, self.controller)
