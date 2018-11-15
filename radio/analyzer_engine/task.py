from resources import *
from notes import *
from commands import TelecommandDataFactory

class TaskData:
    def __init__(self, name, is_scheduled, resources_utilization, notes):
        self.name = name
        self.is_scheduled = is_scheduled
        self.resources_utilization = resources_utilization
        self.notes = notes


class TaskAnalyzer:
    def __init__(self):
        self.telecommand_data_factory = TelecommandDataFactory()

    def is_sleep(self, task):
        send_mode = task[1]
        if send_mode.__name__ == "Sleep":
            return True
        return False
    
    def is_print(self, task):
        send_mode = task[1]
        if send_mode.__name__ == "Print":
            return True
        return False

    def process(self, task, state, limits):
        argument = task[0]
        send_mode = task[1]
        wait_mode = task[2]
        notes = Notes()

        task_resources = Resources.init_with_zeros()

        command_data = self.telecommand_data_factory.get_analyzer(send_mode, argument)
        task_resources.session.uplink.frames_count += command_data.get_uplink_frames_count()
        task_resources.session.downlink.frames_count += command_data.get_downlink_frames_count()
        command_data.process(state, notes, send_mode, wait_mode, limits)

        task_resources.session.uplink.duration = command_data.get_uplink_duration(state.current_uplink_bitrate())
        task_resources.session.downlink.duration = command_data.get_downlink_duration(state.current_downlink_bitrate())
        task_resources.session.power_budget.energy = command_data.get_downlink_energy_consumption(task_resources.session.downlink.duration)

        telecommand_name = command_data.telecommand_name()

        if self.is_sleep(task):
            task_resources = Resources.init_with_zeros()
            telecommand_name = "Sleep {}s".format(str(send_mode.seconds))

        if self.is_print(task):
            task_resources = Resources.init_with_zeros()
            telecommand_name = "Print"

        return TaskData(telecommand_name, command_data.is_scheduled(), task_resources, notes)
