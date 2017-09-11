import time
import serial

class RemotePowerSocket(object):
    def __init__(self, port):
        self.remoteSwitch = serial.Serial(port, 9600)
        time.sleep(5)

    def send_command(self, command):
        time.sleep(0.5)
        self.remoteSwitch.write(b'\x07')
        time.sleep(0.1)
        self.remoteSwitch.write(command)
        time.sleep(0.1)
        self.remoteSwitch.write(b'\x08')
        
    def turn_on_socket_no_1(self):  
        print("Turning on REMOTE CONTROL SOCKET SWITCH no. 1...")
        self.send_command(b'\x0A')
        self.send_command(b'\x0A')
        self.send_command(b'\x0A')

        print("230 V switched ON for SWITCH no. 1!")

    def turn_off_socket_no_1(self):   
        print("Turning off REMOTE CONTROL SOCKET SWITCH no. 1...")
        self.send_command(b'\x15')
        self.send_command(b'\x15')
        self.send_command(b'\x15')

        print("230 V switched OFF for SWITCH no. 1!")

    def turn_on_socket_no_2(self):  
        print("Turning on REMOTE CONTROL SOCKET SWITCH no. 2...")
        self.send_command(b'\x20')
        self.send_command(b'\x20')
        self.send_command(b'\x20')

        print("230 V switched ON for SWITCH no. 2!")

    def turn_off_socket_no_2(self):   
        print("Turning off REMOTE CONTROL SOCKET SWITCH no. 2...")
        self.send_command(b'\x2B')
        self.send_command(b'\x2B')
        self.send_command(b'\x2B')
        
    def turn_on_socket_no_3(self):  
        print("Turning on REMOTE CONTROL SOCKET SWITCH no. 3...")
        self.send_command(b'\x36')
        self.send_command(b'\x36')
        self.send_command(b'\x36')

        print("230 V switched ON for SWITCH no. 3!")

    def turn_off_socket_no_3(self):   
        print("Turning off REMOTE CONTROL SOCKET SWITCH no. 3...")
        self.send_command(b'\x41')
        self.send_command(b'\x41')
        self.send_command(b'\x41')

        print("230 V switched OFF for SWITCH no. 3!")
