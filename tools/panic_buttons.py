import keyboard
import serial
import time


class Action:
    def __init__(self, text_to_write):
        self.text_to_write = text_to_write

        self.last_pressed = False

    def update(self, pressed):
        if self.last_pressed is False and pressed is True:
            # pressed now
            keyboard.write(self.text_to_write)
            print("Pressed! Sending " + self.text_to_write)

        self.last_pressed = pressed


power_cycle = Action('panic_power_cycle()')
detumble = Action('panic_detumbling()')

ser = serial.Serial('COM18')

print("Panic buttons running!")

while True:
    power_cycle.update(not ser.dsr)
    detumble.update(not ser.cts)
    time.sleep(0.1)
