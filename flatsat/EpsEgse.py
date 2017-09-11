import time
import serial

class EpsEgseA(object):
    def __init__(self, port):
        self.epsEgse = serial.Serial(port, 9600)
        time.sleep(2)

    def send_command(self, command):
        time.sleep(0.1)
        self.epsEgse.write(b'\x07')
        time.sleep(0.05)
        self.epsEgse.write(command)
        time.sleep(0.05)
        self.epsEgse.write(b'\x08')
        
    def kill_enable(self):  
        print("Turning on Kill-Switch...")
        self.send_command(b'\x15')
        print("Kill-Switch is ON!")
        
    def kill_disable(self):  
        print("Turning off Kill-Switch...")
        self.send_command(b'\x25')
        print("Kill-Switch is OFF!")

    def rbl_enable(self):  
        print("Turning on RBL...")
        self.send_command(b'\x32')
        print("RBL is ON!")
        
    def rbl_disable(self):  
        print("Turning off RBL...")
        self.send_command(b'\x42')
        print("RBL is OFF!")
