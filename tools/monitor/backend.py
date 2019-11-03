import argparse
import os
import datetime
import pprint
import json

from colorama import Fore, Style, Back
import zmq
from zmq.utils.win32 import allow_interrupt
from collections import OrderedDict

import response_frames
from response_frames.common import FileSendSuccessFrame, FileSendErrorFrame
from utils import ensure_byte_list, ensure_string
from telecommand.fs import DownloadFile 

from gui import MonitorUI
import locale


class MonitorBackend:
    def __init__(self):
        self.Decoder = response_frames.FrameDecoder(response_frames.frame_factories)
        self.abort_push = zmq.Context.instance().socket(zmq.PAIR)
        self.abort_push.bind('inproc://download_monitor/abort')
        self.abort_pull = zmq.Context.instance().socket(zmq.PAIR)
        self.abort_pull.connect('inproc://download_monitor/abort')

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('session', type=int, help='Session number')
        parser.add_argument('address', nargs='+', help='Address to connect for frames')
        parser.add_argument('--port', '-p', help='Command port', type=int, default=7007)
        parser.add_argument('--mission', '-m', help='Mission repo', default=os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mission'))

        return parser.parse_args()

    def connect_sockets(self, addresses):
        ctx = zmq.Context.instance()
        result = []

        for a in addresses:
            socket = ctx.socket(zmq.SUB)
            socket.setsockopt(zmq.SUBSCRIBE, '')
            socket.connect(a)
            result.append(socket)

        return result

    def parse_frame(self, raw_frame):
        return self.Decoder.decode(ensure_byte_list(raw_frame[16:-2]))

    def load_tasklist(self, mission_path, session):
        tasks_file_path = os.path.join(mission_path, 'sessions', str(session), 'tasklist.py')  
        if not os.path.exists(tasks_file_path):
            print("Could not find file {}".format(tasks_file_path))
            return []
    
        import telecommand as tc
        import datetime
        from radio.task_actions import Send, SendLoop, Sleep, Print, SendReceive, WaitMode
        from devices import camera
        from devices.adcs import AdcsMode
        from devices.camera import CameraLocation, PhotoResolution
        from devices.comm import BaudRate
        
        local_values = locals()
        with open(tasks_file_path) as tasks_file:
            exec(tasks_file, globals(), local_values)

        tasks = local_values['tasks']
        return tasks

    def create_dictionary(self, tasklist):
            commandsDict = OrderedDict()

            for item in tasklist:
                command = item[0]
                if not isinstance(command, DownloadFile):
                    continue
                commandsDict[command._correlation_id] = command

            return commandsDict

    def generate_new_tasklist(self, commandsDict):
        newTasks = []
        for _, command in commandsDict.items():
            newTasks.append(command)

        return newTasks

    def process_frame(self, frame, commandsDict, ui):
        if not type(frame) in [FileSendSuccessFrame, FileSendErrorFrame]:
            return

        try:
            tasklistCommandChunks = commandsDict[frame.correlation_id]._seqs
            if frame._seq in tasklistCommandChunks:
                tasklistCommandChunks.remove(frame._seq)
            if len(tasklistCommandChunks) == 0:
                del commandsDict[frame.correlation_id]
        except KeyError:
            pass   

        stamp = datetime.datetime.now().time()
        ui.logFrame(frame, stamp)
        ui.update_tasklist(commandsDict)

    def _get_missings_for_one_task_command(self, correlation_id, commandsDict, socket, ui):
        try:
            task = commandsDict[correlation_id]
            task_string = json.dumps(task.__dict__)
            ui.log("Sending task for file '{}'/{}, length {}.".format(task._path, task._correlation_id, len(task._seqs)))
        except KeyError:
            task_string = ""
            ui.log("No data found for CID {}".format(correlation_id))
        
        socket.send(task_string)

    def _get_tasklist_with_all_missings_command(self, commandsDict, socket, ui):
        tasks = []
        for _, command in commandsDict.items():
            tasks.append(command.__dict__)

        tasks.sort(key=lambda x: ("telemetry" in x['_path'], x['_correlation_id']))
        
        ui.log("Sending new {} tasks.".format(len(tasks)))
        task_string = json.dumps(tasks)
        socket.send(task_string)

    def handle_commands(self, request, commandsDict, socket, ui):
        command = json.loads(request)
        try:
            command_name = command['command']
        except:
            ui.log("Unknown command")
            return

        if command_name == 'GetMissingsForOneTask':
            self._get_missings_for_one_task_command(command['data'], commandsDict, socket, ui)

        elif command_name == 'GetTasklistWithAllMissings':  
            self._get_tasklist_with_all_missings_command(commandsDict, socket, ui)

    def run(self, args):
        import colorama
        colorama.init()
        locale.setlocale(locale.LC_ALL, '')

        sockets = self.connect_sockets(args.address)

        def abort():
            self.abort_push.send('ABORT')

        command_rep = zmq.Context.instance().socket(zmq.REP)
        try:
            command_rep.bind('tcp://0.0.0.0:{}'.format(args.port))
        except:
            print("Can't bind to port {}".format(args.port))

        session = args.session

        tasklist = self.load_tasklist(args.mission, session)
        print("Loaded {} tasks.".format(len(tasklist)))
        commandsDict = self.create_dictionary(tasklist)

        if (len(tasklist) == 0):
            return

        ui = MonitorUI(session, commandsDict, len(tasklist), abort)
        ui_thread = ui.run()

        with allow_interrupt(abort):
            while True:
                try:
                    (read, _, _) = zmq.select(sockets + [self.abort_pull] + [command_rep], [], [])
                except KeyboardInterrupt:
                    ui.log("Ending...")
                    break

                if self.abort_pull in read:
                    break

                if command_rep in read:
                    self.handle_commands(command_rep.recv(), commandsDict, command_rep, ui)
                    continue

                for ready in read:
                    frame = ready.recv()
                    frame = self.parse_frame(frame)
                    self.process_frame(frame, commandsDict, ui)

        ui.stop()
        ui_thread.join()

