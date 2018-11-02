from resources import *
from notes import *
from commands import TelecommandDataFactory
from task_actions import WaitMode

class TaskData:
    def __init__(self, name, is_scheduled, bitrate_index, resources_utilization, notes):
        self.name = name
        self.is_scheduled = is_scheduled
        self.bitrate_index = bitrate_index
        self.resources_utilization = resources_utilization
        self.notes = notes


class TaskAnalyzer:
    BITRATE_MAP = [0, 1200, 2400, 0, 4800, 0, 0, 0, 9600]
    DOWNLINK_MAX_FRAME_SIZE = 235
    UPLINK_BITRATE = 1200
    MAX_PATH_LENGTH = 100
    MAX_DOWNLOAD_CHUNKS = 38
    TASK_FRAME_OFFSET = 0
    FRAME_PAYLOAD_OFFSET = 1

    @classmethod
    def process(self, task, bitrate_index=1):
        frame = task[0]
        send_mode = task[1]
        wait_mode = task[2]

        correlation_ids = []

        task_resources = Resources.init_with_zeros()

        task_resources.session.uplink.frames_count += 1
        task_resources.session.downlink.frames_count += 1

        downlink_bitrate = self.to_bitrate(bitrate_index)

        notes = Notes()

        telecommand_data_factory = TelecommandDataFactory()
        command_data = telecommand_data_factory.get_telecommand_data(frame)

        correlation_id = command_data.get_correlation_id()
        if correlation_id is not None:
            if correlation_id in correlation_ids:
                notes.error('Duplicate correlation id = {}'.format(correlation_id))
            correlation_ids.append(correlation_id)

        if command_data.get_requires_wait() and wait_mode != WaitMode.Wait:
            notes.warning('Wait suggested')

        if command_data.get_requires_send_receive() and send_mode != 'SendReceive':
            notes.warning('SendReceive suggested')

        if self.get_task_name(task) == 'OpenSailTelecommand':
            notes.warning('Did you mean: PerformSailExperiment?')

        if self.get_task_name(task) == 'SetBitrate':
            payload = command_data.get_payload()
            if payload[1] not in [1, 2, 4, 8]:
                notes.error('Wrong bitrate value')
            else:
                self.bitrate_index = payload[1]

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
        task_resources.session.downlink.duration = command_data.get_downlink_duration(downlink_bitrate)
        task_resources.session.power_budget.energy = command_data.get_downlink_energy_consumption(task_resources.session.downlink.duration)

        return TaskData(self.get_task_name(task), self.is_scheduled(task), bitrate_index, task_resources, notes)

    @classmethod
    def update_bitrate_index(self, task, current_bitrate_index):
        new_bitrate_index = current_bitrate_index

        if self.get_task_name(task) == "SetBitrate":
            frame = task[self.TASK_FRAME_OFFSET]
            telecommand_data_factory = TelecommandDataFactory()
            new_bitrate_index = telecommand_data_factory.get_telecommand_data(frame).get_payload()[self.FRAME_PAYLOAD_OFFSET]

        if self.get_task_name(task) == "PowerCycleTelecommand":
            new_bitrate_index = 1

        if self.get_task_name(task) == "ResetTransmitterTelecommand":
            new_bitrate_index = 1

        return new_bitrate_index

    @classmethod
    def to_bitrate(self, bitrate_index):
        return self.BITRATE_MAP[bitrate_index]

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



