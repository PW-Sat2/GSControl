import argparse
import os
import datetime
import json

import zmq
from zmq.utils.win32 import allow_interrupt
from collections import OrderedDict

import response_frames
from utils import ensure_byte_list
from telecommand.fs import DownloadFile 
from telecommand.memory import ReadMemory
from telecommand.program_upload import WriteProgramPart

from gui import MonitorUI
from model import (DownloadFileTask, DownloadFrameView, MemoryTask, MemoryFrameView, 
    FileListFrameView, WriteProgramPartTask, WriteProgramPartSuccessFrameView)

class MonitorBackend:
    def __init__(self, args):
        self.Decoder = response_frames.FrameDecoder(response_frames.frame_factories)

        ctx = zmq.Context.instance()
        self.abort_push = ctx.socket(zmq.PAIR)
        self.abort_pull = ctx.socket(zmq.PAIR)
        self.command_socket = ctx.socket(zmq.REP)
        self.command_bound = False

        self.session = args.session
        self.endpoints = args.address
        self.port = args.port
        self.mission_path = args.mission

        self.ui = None
        self.listening_sockets = None
        self.download_tasks = None
 
        self.abort_push.bind('inproc://download_monitor/abort')
        self.abort_pull.connect('inproc://download_monitor/abort')       

    @staticmethod
    def parse_args():
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

            for index, item in enumerate(tasklist, start=1):
                command = item[0]
                if isinstance(command, DownloadFile):
                    commandsDict[command.correlation_id()] = DownloadFileTask.create_from_task(command, index)
                elif isinstance(command, ReadMemory):
                    commandsDict[command.correlation_id()] = MemoryTask.create_from_task(command, index)
                elif isinstance(command, WriteProgramPart):
                    task = WriteProgramPartTask.create_from_task(command, index)
                    correlation_id = task.get_dummy_correlation_id()
                    commandsDict[correlation_id] = task
                else:
                    continue

            return commandsDict

    def _process_file_list_frame(self, frame):
        frameView = FileListFrameView.create_from_frame(frame)  
        stamp = datetime.datetime.now().time()
        self.ui.logFileListFrame(frameView, stamp)

    def process_frame(self, frame):
        frameView = None
        if DownloadFrameView.is_download_frame(frame):
            frameView = DownloadFrameView.create_from_frame(frame)
        elif MemoryFrameView.is_memory_frame(frame):
            frameView = MemoryFrameView.create_from_frame(frame)
        elif WriteProgramPartSuccessFrameView.is_write_program_frame(frame):
            frameView = WriteProgramPartSuccessFrameView.create_from_frame(frame)
        elif FileListFrameView.is_file_list_frame(frame):
            self._process_file_list_frame(frame)
            return
        else:
            return

        try:
            tasklistCommandChunks = self.download_tasks[frameView.correlation_id].chunks
            if frameView.chunk in tasklistCommandChunks:
                tasklistCommandChunks.remove(frameView.chunk)
            if len(tasklistCommandChunks) == 0:
                del self.download_tasks[frameView.correlation_id]
        except KeyError:
            pass   

        stamp = datetime.datetime.now().time()
        self.ui.logFrame(frameView, stamp)
        self.ui.update_tasklist(self.download_tasks)

    def _get_missings_for_one_task_command(self, correlation_id):
        try:
            task = self.download_tasks[correlation_id]
            if isinstance(task, DownloadFileTask):
                task_string = json.dumps(task.to_dict())
                self.ui.log("Sending task for file '{}'/{}, length {}.".format(task.path, task.correlation_id, task.length()))
            else:
                task_string = ""
                self.ui.log("Not supported task CID {}".format(correlation_id))
        except KeyError:
            task_string = ""
            self.ui.log("No data found for CID {}".format(correlation_id))
        
        self.command_socket.send(task_string)

    def _get_tasklist_with_all_missings_command(self):
        tasks = []
        for _, command in self.download_tasks.items():
            if isinstance(command, DownloadFileTask):
                tasks.append(command.to_dict())

        tasks.sort(key=lambda x: ("telemetry" in x['path'], x['correlation_id']))
        
        self.ui.log("Sending new {} tasks.".format(len(tasks)))
        task_string = json.dumps(tasks)
        self.command_socket.send(task_string)

    def handle_commands(self, request):
        command = json.loads(request)
        try:
            command_name = command['command']
        except:
            self.ui.log("Unknown command")
            return

        if command_name == 'GetMissingsForOneTask':
            self._get_missings_for_one_task_command(command['data'])

        elif command_name == 'GetTasklistWithAllMissings':  
            self._get_tasklist_with_all_missings_command()

    def abort(self):
            self.abort_push.send('ABORT')

    def run(self):
        self.listening_sockets = self.connect_sockets(self.endpoints)
   
        try:
            self.command_socket.bind('tcp://0.0.0.0:{}'.format(self.port))
            self.command_bound = True
        except:
            print("Can't bind to port {}".format(self.port))

        tasklist = self.load_tasklist(self.mission_path, self.session)
        original_tasklist_length = len(tasklist)
        print("Loaded {} tasks.".format(original_tasklist_length))
        self.download_tasks = self.create_dictionary(tasklist)

        if original_tasklist_length == 0:
            return

        self.ui = MonitorUI(self.session, self.download_tasks, original_tasklist_length, self.abort, self.command_bound)
        ui_thread = self.ui.run()

        with allow_interrupt(self.abort):
            while True:
                try:
                    (read, _, _) = zmq.select(self.listening_sockets + [self.abort_pull] + [self.command_socket], [], [])
                except KeyboardInterrupt:
                    self.ui.log("Ending...")
                    break

                if self.abort_pull in read:
                    break

                if self.command_socket in read:
                    self.handle_commands(self.command_socket.recv())
                    continue

                for ready in read:
                    frame = ready.recv()
                    frame = self.parse_frame(frame)
                    self.process_frame(frame)

        self.ui.stop()
        ui_thread.join()

    @staticmethod
    def main():
        import locale
        locale.setlocale(locale.LC_ALL, '')

        args = MonitorBackend.parse_args()
        monitor = MonitorBackend(args)
        monitor.run()

