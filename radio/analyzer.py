from tabulate import tabulate
from colorama import init, Fore, Style
from telecommand_data.commands import TelecommandDataFactory
from telecommand_data.duration import Duration

init()

max_downlink_frame_size = 235
max_download_seq_amount = 38
max_path_length = 100
frame_size = 8 # bits
bitrate_map = [0, 1200, 2400, 0, 4800, 0, 0, 0, 9600]
uplink_bitrate = 1200

class Notes(list):
    def warning(self, text):
        self.append(Fore.YELLOW + 'Warning: ' + text + Style.RESET_ALL)

    def error(self, text):
        self.append(Fore.RED + 'Error: ' + text + Style.RESET_ALL)

    def info(self, text):
        self.append(Fore.CYAN + 'Info: ' + text + Style.RESET_ALL)

command_durations = dict({
    'DownloadFile': Duration(10, 25)
})

class TaskData:
    def __init__(self, name, notes, payload_size, uplink_duration, downlink_duration):
        self.name = name
        self.notes = notes
        self.payload_size = payload_size
        self.uplink_duration = uplink_duration
        self.downlink_duration = downlink_duration

class Analyzer:
    def __init__(self, tasks, bitrate_index):
        self.tasks = tasks
        self.correlation_ids = []
        self.initial_bitrate_index = bitrate_index
        self.bitrate_index = bitrate_index
        self.upload_frames = 0
        self.download_frames = 0

    def run(self):
        result = [[]]
        overall_uplink_duration = Duration(0)
        overall_downlink_duration = Duration(0)
        index = 1
        for task in self.tasks:
            task_data = self.process_task(task)

            result.append([
                index,
                task_data.name,
                task_data.payload_size,
                str(task_data.uplink_duration),
                str(task_data.downlink_duration),
                '\n'.join(task_data.notes)
            ])

            overall_uplink_duration += task_data.uplink_duration
            overall_downlink_duration += task_data.downlink_duration
            index += 1

        print Style.RESET_ALL + tabulate(result, headers=[
            '#',
            'Name',
            'Payload size',
            'Up Duration',
            'Down Duration',
            'Notes'
        ])
        print

        if self.bitrate_index != self.initial_bitrate_index:
            print Fore.YELLOW + 'Warning: Bitrate not restored ({})'.format(self.initial_bitrate_index)\
                  + Style.RESET_ALL
        print 'Uplink frames count: {}'.format(self.upload_frames)
        print 'Downlink frames count: {}'.format(self.download_frames)
        print 'Uplink duration: {}'.format(str(overall_uplink_duration))
        print 'Downlink duration: {}'.format(str(overall_downlink_duration))

    def process_task(self, task):
        frame = task[0]
        send_mode = task[1]
        wait_mode = task[2]

        self.upload_frames += 1
        self.download_frames += 1

        downlink_bitrate = bitrate_map[self.bitrate_index]

        notes = Notes()

        telecommand_data_factory = TelecommandDataFactory()
        command_data = telecommand_data_factory.get_telecommand_data(frame)
        print type(command_data).__name__
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
            notes.warning('Did you mean: PerformSailExperiment')

        if command_data.telecommand_name() == 'SetBitrate':
            payload = command_data.get_payload()
            if payload[1] not in [1, 2, 4, 8]:
                notes.error('Wrong bitrate value')
            else:
                self.bitrate_index = payload[1]

        if command_data.telecommand_name() == 'DownloadFile':
            payload = command_data.get_payload()
            path_length = payload[1]
            if path_length > max_path_length:
                notes.error('Path too long')
            seqs = payload[(path_length + 3):]
            seqs_count = len(seqs) / 4
            if seqs_count / 4 > max_download_seq_amount:
                notes.error('Too many sequences to download')
            self.download_frames += seqs_count

        if command_data.get_payload_size() > max_downlink_frame_size:
            notes.error('Payload too big')

        for extra_note in command_data.get_extra_notes():
            notes.info(extra_note)

        uplink_duration = command_data.get_uplink_duration(uplink_bitrate)
        downlink_duration = command_data.get_downlink_duration(downlink_bitrate)
        return TaskData(command_data.telecommand_name(), notes, command_data.get_payload_size(), uplink_duration, downlink_duration)

if __name__ == '__main__':
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    import telecommand as tc

    test_tasks = [
        [tc.SetBitrate(1, 8), "SendReceive", "NoWait"],
        [tc.SendBeacon(), "SendReceive", "NoWait"],
        [tc.SendBeacon(), "Send", "NoWait"],
        [tc.ListFiles(1, '/'), "Send", "NoWait"],
        [tc.ResetTransmitterTelecommand(), "Send", "NoWait"],
        [tc.DownloadFile(17, '/telemetry.current', [i for i in range(0, 240, 7)]), "Send", "Wait"],
        [tc.DownloadFile(18, '/telemetry.current', [i for i in range(240, 480, 7)]), "Send", "Wait"],
        [tc.DownloadFile(19, '/telemetry.current', [i for i in range(480, 720, 7)]), "Send", "Wait"],
        [tc.DownloadFile(20, '/telemetry.current', [i for i in range(720, 960, 7)]), "Send", "Wait"],
        [tc.SendBeacon(), "Send", "NoWait"],
        [tc.SendBeacon(), "Send", "NoWait"],
        [tc.SetBitrate(1, 1), "SendReceive", "Nowait"]
    ]

    analyzer = Analyzer(test_tasks, 1)
    analyzer.run()
