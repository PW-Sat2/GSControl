import time
import sys
sys.path.insert(0, 'flatsat')
from Flatsat import SolarPanelsSimulator

simulator = SolarPanelsSimulator()
simulator.random_tumbling(min_rotation_speed = 20, max_rotation_speed = 25, solar_panels_are_deployed = True, sail_is_deployed = True)

time.sleep(10)
