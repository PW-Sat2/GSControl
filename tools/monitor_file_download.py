import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitor.backend import MonitorBackend

monitor = MonitorBackend()
monitor.run(monitor.parse_args())
