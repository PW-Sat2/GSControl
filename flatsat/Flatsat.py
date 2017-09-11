#import sys
#import os
#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import time
from time import localtime, strftime
from PowerSupply import PowerSupply
from RemotePowerSocket import RemotePowerSocket
from Config import config
from EpsEgse import EpsEgseA
from ObcReset import ObcReset

class Flatsat(object):
    def power_on(self):
        power_socket = RemotePowerSocket(config.get("REMOTE_POWER_SOCKET_COM"))
        power_socket.turn_on_socket_no_1()
        power_socket.turn_on_socket_no_3()
        time.sleep(10)

        usb_power_supply = PowerSupply("USB", config.get("USB_POWER_SUPPLY_COM"), config.get("USB_POWER_SUPPLY_SN"))
        usb_power_supply.set_outputs([0, 0], [10.0, 0.6], [5.0, 0.9])
        usb_power_supply.turn_on()

        print("Waiting 15s for USB devices...")
        time.sleep(15)

        eps_egse = EpsEgseA(config.get("EPS_EGSE_A_COM"))
        eps_egse.kill_disable()
        eps_egse.rbl_disable()
        eps_egse.kill_enable()
        eps_egse.rbl_enable()

        eps_power_supply = PowerSupply("EPS", config.get("EPS_POWER_SUPPLY_COM"), config.get("EPS_POWER_SUPPLY_SN"))
        eps_power_supply.set_outputs([10.5, 0.600], [10.5, 0.600], [5.5, 0.484])
        eps_power_supply.turn_on()

        time.sleep(5)

        obc_reset_control = ObcReset(config.get("OBC_RESET_COM"))
        obc_reset_control.perform_reset()

        print("Success! Flatsat is ON at "+ strftime("%Y-%m-%d", localtime()) + " " + strftime("%H:%M:%S", localtime()) + "!")

    def power_off(self):
        eps_power_supply = PowerSupply("EPS", config.get("EPS_POWER_SUPPLY_COM"), config.get("EPS_POWER_SUPPLY_SN"))
        eps_power_supply.set_zeros()
        eps_power_supply.turn_off()

        eps_egse = EpsEgseA(config.get("EPS_EGSE_A_COM"))
        eps_egse.kill_disable()
        eps_egse.rbl_disable()

        usb_power_supply = PowerSupply("USB", config.get("USB_POWER_SUPPLY_COM"), config.get("USB_POWER_SUPPLY_SN"))
        usb_power_supply.set_zeros()
        usb_power_supply.turn_off()

        time.sleep(5)

        power_socket = RemotePowerSocket(config.get("REMOTE_POWER_SOCKET_COM"))
        power_socket.turn_off_socket_no_1()
        power_socket.turn_off_socket_no_3()

        print("Success! Flatsat is OFF at "+ strftime("%Y-%m-%d", localtime()) + " " + strftime("%H:%M:%S", localtime()) + "!")
