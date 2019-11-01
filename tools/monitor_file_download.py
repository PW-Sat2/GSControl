from monitor.backend import MonitorBackend

monitor = MonitorBackend()
monitor.run(monitor.parse_args())
