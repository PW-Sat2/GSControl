from resources import *
from commands import TelecommandDataFactory
from colorama import init, Fore, Style

class TaskData:
    def __init__(self, name, bitrate_index, resources_utilization, notes):
        self.name = name
        self.bitrate_index = bitrate_index
        self.resources_utilization = resources_utilization
        self.notes = notes


class TaskAnalyzer:
    BITRATE_MAP = [0, 1200, 2400, 0, 4800, 0, 0, 0, 9600]
    correlation_ids = []
    DOWNLINK_MAX_FRAME_SIZE = 235
    uplink_bitrate = 1200
    max_path_length = 100
    max_download_seq_amount = 38

    TASK_FRAME_OFFSET = 0
    FRAME_PAYLOAD_OFFSET = 1

    @classmethod
    def process(self, task, bitrate_index=1):
        frame = task[0]
        send_mode = task[1]
        wait_mode = task[2]

        task_resources = Resources.init_with_zeros()

        task_resources.session.uplink.frames_count += 1
        task_resources.session.downlink.frames_count += 1

        downlink_bitrate = self.to_bitrate(bitrate_index)

        notes = Notes()

        telecommand_data_factory = TelecommandDataFactory()
        command_data = telecommand_data_factory.get_telecommand_data(frame)
        #print type(command_data).__name__
        correlation_id = command_data.get_correlation_id()
        if correlation_id is not None:
            if correlation_id in self.correlation_ids:
                notes.error('Duplicate correlation id = {}'.format(correlation_id))
            self.correlation_ids.append(correlation_id)

        if command_data.get_requires_wait() and wait_mode != 'Wait':
            notes.warning('Wait suggested')

        if command_data.get_requires_send_receive() and send_mode != 'SendReceive':
            notes.warning('SendReceive suggested')

        if command_data.telecommand_name() == 'OpenSailTelecommand':
            notes.warning('Did you mean: PerformSailExperiment?')

        if command_data.telecommand_name() == 'SetBitrate':
            payload = command_data.get_payload()
            if payload[1] not in [1, 2, 4, 8]:
                notes.error('Wrong bitrate value')
            else:
                self.bitrate_index = payload[1]

        if command_data.telecommand_name() == 'DownloadFile':
            payload = command_data.get_payload()
            path_length = payload[1]
            if path_length > self.max_path_length:
                notes.error('Path too long')
            seqs = payload[(path_length + 3):]
            seqs_count = len(seqs) / 4
            if seqs_count / 4 > self.max_download_seq_amount:
                notes.error('Too many sequences to download')
            task_resources.session.downlink.frames_count += seqs_count

        if command_data.get_payload_size() > self.DOWNLINK_MAX_FRAME_SIZE:
            notes.error('Payload too big')

        for extra_note in command_data.get_extra_notes():
            notes.info(extra_note)

        task_resources.session.uplink.duration = command_data.get_uplink_duration(self.uplink_bitrate)
        task_resources.session.downlink.duration = command_data.get_downlink_duration(downlink_bitrate)

        return TaskData(command_data.telecommand_name(), bitrate_index, task_resources, notes)

    @classmethod
    def update_bitrate_index(self, task, current_bitrate_index):
        task_data = TaskAnalyzer.process(task, current_bitrate_index)

        new_bitrate_index = current_bitrate_index

        if task_data.name == "SetBitrate":
            frame = task[self.TASK_FRAME_OFFSET]
            telecommand_data_factory = TelecommandDataFactory()
            new_bitrate_index = telecommand_data_factory.get_telecommand_data(frame).get_payload()[self.FRAME_PAYLOAD_OFFSET]

        if task_data.name == "PowerCycleTelecommand":
            new_bitrate_index = 1

        if task_data.name == "ResetTransmitterTelecommand":
            new_bitrate_index = 1

        return new_bitrate_index

    @classmethod
    def to_bitrate(self, bitrate_index):
        return self.BITRATE_MAP[bitrate_index]

    @classmethod
    def is_experiment(self, task):
        task_data = TaskAnalyzer.process(task)

        if task_data.name == "TakePhotoTelecommand":
            return True

        return False

class Notes(list):
    def warning(self, text):
        self.append(Fore.YELLOW + '[Warning] ' + text + Style.RESET_ALL)

    def error(self, text):
        self.append(Fore.RED + '[Error] ' + text + Style.RESET_ALL)

    def info(self, text):
        self.append(Fore.CYAN + '[Info] ' + text + Style.RESET_ALL)
