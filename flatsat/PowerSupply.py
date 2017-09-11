import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'LPS305B'))

from LS305B import LS305B
import serial
import time

class PowerSupply(object):
    def __init__(self, supplied_device_name, serial_port_number, power_supply_sn):
        self.power_supply = LS305B(serial_port_number)
        self.expected_serial_number = power_supply_sn
        self.supplied_device_name = supplied_device_name

        self.power_supply.set_remote()
        self.power_supply.reset()
        self.power_supply.disable_output()

        if not self.is_power_supply_sn_matched(self.expected_serial_number):
            sys.exit("Fatal error: wrong serial number for BK LPS305B-TC for "+self.supplied_device_name+".");

        print "Power sypply for "+self.supplied_device_name+": BK LPS305B-TC SN "+self.expected_serial_number
        print "Power sypply for "+self.supplied_device_name+": initialization OK!"

    def get_power_supply_sn(self):
        get_idn_result = self.power_supply.get_idn()
        get_idn_result = get_idn_result.split(', ')
        actual_power_supply_sn = get_idn_result[2]
        return actual_power_supply_sn

    def is_power_supply_sn_matched(self, expected_serial_number):
        if expected_serial_number==self.get_power_supply_sn():
            return True
        return False

    def set_outputs(self, setup_ch1, setup_ch2, setup_ch3):
        print("Power sypply for "+self.supplied_device_name+": setting voltages and current limits...")
        print("\tCH1->" + str(setup_ch1[0]) + "V/" + str(setup_ch1[1]) + 
        "A    CH2->" + str(setup_ch2[0]) + "V/" + str(setup_ch2[1]) +
        "A    CH3->" + str(setup_ch3[0]) + "V/" + str(setup_ch3[1]) + "A")

        self.power_supply.set(LS305B.Channel.CH1, setup_ch1[0], setup_ch1[1])
        self.power_supply.set(LS305B.Channel.CH2, setup_ch2[0], setup_ch2[1])
        self.power_supply.set(LS305B.Channel.CH3, setup_ch3[0], setup_ch3[1])

    def set_zeros(self):
        self.set_outputs([0, 0], [0, 0], [0, 0])
    
    def turn_on(self):
        self.power_supply.enable_output()
        print("Power sypply for "+self.supplied_device_name+": outputs enabled.")

    def turn_off(self):
        self.power_supply.disable_output()
        print("Power sypply for "+self.supplied_device_name+": outputs disabled.")
