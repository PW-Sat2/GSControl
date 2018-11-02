from resources import *
from notes import *
from commands import TelecommandDataFactory
from task_actions import WaitMode, SendReceive

class TaskData:
    def __init__(self, name, is_scheduled, resources_utilization, notes):
        self.name = name
        self.is_scheduled = is_scheduled
        self.resources_utilization = resources_utilization
        self.notes = notes


class TaskAnalyzer:
    MAX_PATH_LENGTH = 100
    MAX_DOWNLOAD_CHUNKS = 38

    def __init__(self):
        self.telecommand_data_factory = TelecommandDataFactory()

    def process(self, task, state, limits):
        frame = task[0]
        send_mode = task[1]
        wait_mode = task[2]
        notes = Notes()

        task_resources = Resources.init_with_zeros()

        task_resources.session.uplink.frames_count += 1
        task_resources.session.downlink.frames_count += 1

        command_data = self.telecommand_data_factory.get_telecommand_data(frame)
        command_data.process(state, notes, send_mode, wait_mode, limits)

        if command_data.get_requires_wait() and wait_mode != WaitMode.Wait:
            notes.warning('Wait suggested')

        if command_data.get_requires_send_receive() and send_mode != SendReceive:
            notes.warning('SendReceive suggested')

        task_resources.session.uplink.duration = command_data.get_uplink_duration(state.current_uplink_bitrate())
        task_resources.session.downlink.duration = command_data.get_downlink_duration(state.current_downlink_bitrate())
        task_resources.session.power_budget.energy = command_data.get_downlink_energy_consumption(task_resources.session.downlink.duration)

        return TaskData(command_data.telecommand_name(), command_data.is_scheduled(), task_resources, notes)



