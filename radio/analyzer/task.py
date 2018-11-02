from resources import *
from notes import *
from commands import TelecommandDataFactory
from task_actions import WaitMode

class TaskData:
    def __init__(self, name, is_scheduled, resources_utilization, notes):
        self.name = name
        self.is_scheduled = is_scheduled
        self.resources_utilization = resources_utilization
        self.notes = notes


class TaskAnalyzer:
    DOWNLINK_MAX_FRAME_SIZE = 235
    UPLINK_BITRATE = 1200
    MAX_PATH_LENGTH = 100
    MAX_DOWNLOAD_CHUNKS = 38
    TASK_FRAME_OFFSET = 0
    FRAME_PAYLOAD_OFFSET = 1

    @classmethod
    def process(self, task, state):
        frame = task[0]
        send_mode = task[1]
        wait_mode = task[2]

        correlation_ids = []

        task_resources = Resources.init_with_zeros()

        task_resources.session.uplink.frames_count += 1
        task_resources.session.downlink.frames_count += 1

        notes = Notes()

        telecommand_data_factory = TelecommandDataFactory()
        command_data = telecommand_data_factory.get_telecommand_data(frame)

        command_data.process(state, notes, send_mode, wait_mode)

        if command_data.get_requires_wait() and wait_mode != WaitMode.Wait:
            notes.warning('Wait suggested')

        if command_data.get_requires_send_receive() and send_mode != 'SendReceive':
            notes.warning('SendReceive suggested')

        if self.get_task_name(task) == 'OpenSailTelecommand':
            notes.warning('Did you mean: PerformSailExperiment?')

        if self.get_task_name(task) == 'DownloadFile':
            payload = command_data.get_payload()
            path_length = payload[1]
            if path_length > self.MAX_PATH_LENGTH:
                notes.error('Path too long')
            seqs = payload[(path_length + 3):]
            seqs_count = len(seqs) / 4
            if seqs_count / 4 > self.MAX_DOWNLOAD_CHUNKS:
                notes.error('Too many sequences to download')
            task_resources.session.downlink.frames_count += seqs_count

        if command_data.get_payload_size() > self.DOWNLINK_MAX_FRAME_SIZE:
            notes.error('Payload too big')

        for extra_note in command_data.get_extra_notes():
            notes.info(extra_note)

        task_resources.session.uplink.duration = command_data.get_uplink_duration(self.UPLINK_BITRATE)
        task_resources.session.downlink.duration = command_data.get_downlink_duration(state.current_downlink_bitrate())
        task_resources.session.power_budget.energy = command_data.get_downlink_energy_consumption(task_resources.session.downlink.duration)

        return TaskData(self.get_task_name(task), self.is_scheduled(task), task_resources, notes)

    @classmethod
    def is_scheduled(self, task):
        if self.get_task_name(task) == "TakePhotoTelecommand":
            return True
        
        if self.get_task_name(task) == "PerformPayloadCommissioningExperiment":
            return True

        return False
    
    @classmethod
    def get_task_name(self, task):
        frame = task[0]

        telecommand_data_factory = TelecommandDataFactory()
        command_data = telecommand_data_factory.get_telecommand_data(frame)

        return command_data.telecommand_name()



