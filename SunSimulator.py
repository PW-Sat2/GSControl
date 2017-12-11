import time
import sys
sys.path.insert(0, 'flatsat')
from Flatsat import SolarPanelsSimulator

simulator = SolarPanelsSimulator()
simulator.random_tumbling(max_rotation_speed = 5, solar_panels_are_deployed = False, sail_is_deployed = False)

time.sleep(10)
