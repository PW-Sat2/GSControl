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
from pyquaternion import Quaternion
import math
import random

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
        eps_power_supply.set_outputs([12.0, 0.6], [12.0, 0.6], [5.5, 0.6])
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

class SolarPanelsSimulator(object):
    MAX_MPPTX_SOLAR_CURRENT = 0.484
    MAX_MPPTYP_SOLAR_CURRENT = 0.484
    MAX_MPPTYN_SOLAR_CURRENT = 0.484
    SAMPLES_PER_SECOND = 10.0

    def clamp(self, to_calmp):
        if to_calmp >= 0:
            return to_calmp
        return 0
        
    def random_tumbling(self, max_rotation_speed = 5, solar_panels_are_deployed = False):
        eps_power_supply = PowerSupply("EPS", config.get("EPS_POWER_SUPPLY_COM"), config.get("EPS_POWER_SUPPLY_SN"))
        eps_power_supply.set_outputs([12.0, 0], [12.0, 0], [6.0, 0])
        eps_power_supply.turn_on()

        while True:
            rotation_x_speed = random.uniform(-max_rotation_speed, max_rotation_speed)
            rotation_y_speed = random.uniform(-max_rotation_speed, max_rotation_speed)
            rotation_z_speed = random.uniform(-max_rotation_speed, max_rotation_speed)
            print "New quaternion angles:", rotation_x_speed, rotation_y_speed, rotation_z_speed

            quaternion_x = Quaternion(axis = [1, 0, 0], angle = math.radians(rotation_x_speed / self.SAMPLES_PER_SECOND))
            rotated_x = quaternion_x.rotate(Quaternion(vector=[0, 0, 1]))
            quaternion_y = Quaternion(axis = [0, 1, 0], angle = math.radians(rotation_y_speed / self.SAMPLES_PER_SECOND))
            rotated_y = quaternion_y.rotate(Quaternion(vector=[1, 0, 0]))
            quaternion_z = Quaternion(axis = [0, 0, 1], angle = math.radians(rotation_z_speed / self.SAMPLES_PER_SECOND))
            rotated_z = quaternion_z.rotate(Quaternion(vector=[0, 1, 0]))

            tstart = time.time()
            while (time.time() - tstart) < (54 * 60):
                rotated_x = quaternion_x.rotate(rotated_x)
                rotated_y = quaternion_y.rotate(rotated_y)
                rotated_z = quaternion_z.rotate(rotated_z)
                rotated_x_y_z = rotated_x * rotated_y * rotated_z

                panel_xp = self.clamp(rotated_x_y_z.vector[0])
                panel_xn = self.clamp(-rotated_x_y_z.vector[0])

                if solar_panels_are_deployed:
                    panel_yp = self.clamp(rotated_x_y_z.vector[0])
                    panel_yn = self.clamp(rotated_x_y_z.vector[0])
                else:
                    panel_yp = self.clamp(rotated_x_y_z.vector[1])
                    panel_yn = self.clamp(-rotated_x_y_z.vector[1])
    
                new_current_value_x = round((panel_xp + panel_xn) * self.MAX_MPPTX_SOLAR_CURRENT, 3)
                new_current_value_yp = round(panel_yp * self.MAX_MPPTYP_SOLAR_CURRENT, 3)
                new_current_value_yn = round(panel_yn * self.MAX_MPPTYN_SOLAR_CURRENT, 3)
    
                eps_power_supply.set_outputs([12.0, new_current_value_yn], [12.0, new_current_value_yp], [6.0, new_current_value_x])

                time.sleep(1.0 / self.SAMPLES_PER_SECOND);
    
            print "Waiting 36min..."
            eps_power_supply.set_outputs([12.0, 0], [12.0, 0], [6.0, 0])
            time.sleep(36 * 60)