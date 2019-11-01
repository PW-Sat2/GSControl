import argparse
import os
import sys
import datetime
import pprint
import json

from colorama import Fore, Style, Back
import zmq
from zmq.utils.win32 import allow_interrupt
from collections import OrderedDict

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import response_frames
from utils import ensure_byte_list, ensure_string
from telecommand.fs import DownloadFile 

from monitor_file_download_gui import MonitorUI
import locale

locale.setlocale(locale.LC_ALL, '')

Decoder = response_frames.FrameDecoder(response_frames.frame_factories)

last_cid = 0

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('session', nargs=1, help='Session number')
    parser.add_argument('address', nargs='+', help='Address to connect for frames')
    parser.add_argument('--port', '-p', help='Command port', type=int, default=7007)
    parser.add_argument('--mission', '-m', help='Mission repo', default=os.path.join(os.path.dirname(__file__), '..', '..', 'mission'))

    return parser.parse_args()


def connect_sockets(addresses):
    ctx = zmq.Context.instance()
    result = []

    for a in addresses:
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, '')
        socket.connect(a)

        result.append(socket)

    return result


def parse_frame(raw_frame):
    return Decoder.decode(ensure_byte_list(raw_frame[16:-2]))

def load_tasklist(mission_path, session):
    tasks_file_path = os.path.join(mission_path, 'sessions', str(session), 'tasklist.py')  
 
    import telecommand as tc
    import datetime
    from radio.task_actions import Send, SendLoop, Sleep, Print, SendReceive, WaitMode
    from devices import camera
    from devices.adcs import AdcsMode
    from devices.camera import CameraLocation, PhotoResolution
    from devices.comm import BaudRate
    
    if not os.path.exists(tasks_file_path):
        print("Could not find file {}".format(tasks_file_path))
        return []

    with open(tasks_file_path) as tasks_file:
        exec(tasks_file)
        tasks_file.close()

    return tasks

def create_dictionary(tasklist):
        commandsDict = OrderedDict()

        for item in tasklist:
            command = item[0]
            if not isinstance(command, DownloadFile):
                continue
            commandsDict[command._correlation_id] = command

        return commandsDict

def generate_new_tasklist(commandsDict):
    newTasks = []
    for _, command in commandsDict.items():
        newTasks.append(command)

    return newTasks

def logFrame(ui, message):
    ui.logFrame(message)
    print(message)

def process_frame(already_received, frame, commandsDict, ui):
    global last_cid
    if not isinstance(frame, response_frames.common.FileSendSuccessFrame) and not isinstance(frame, response_frames.common.FileSendErrorFrame):
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
    timestamp_str = '\x1b[36m{}\x1b[0m'.format(stamp.strftime('%H:%M:%S'))
    print("{} {}".format(timestamp_str, pprint.pformat(frame)))
    ui.logFrame(frame, stamp)
    ui.update_tasklist(commandsDict)

def handle_commands(request, commandsDict, socket, ui):
    command = json.loads(request)

    if command[0] == 'M':
        correlation_id = command[1]
        try:
            task = commandsDict[correlation_id]
            task_string = json.dumps(task.__dict__)
            ui.log("Sending task for file '{}'/{}, length {}.".format(task._path, task._correlation_id, len(task._seqs)))
        except KeyError:
            task_string = ""
            ui.log("No data found for CID {}".format(correlation_id))
        
        socket.send(task_string)
    elif command[0] == 'T':  
        tasks = []
        telemetryTasks = []
        for _, command in commandsDict.items():
            if "telemetry" in command._path:
                telemetryTasks.append(command)
            else:
                tasks.append(command.__dict__)

        # move telemetry to the end - it has less priority
        for telemetryCommand in telemetryTasks:
            tasks.append(telemetryCommand.__dict__)
        
        ui.log("Sending new {} tasks.".format(len(tasks)))
        task_string = json.dumps(tasks)
        socket.send(task_string)


def run(args):
    import colorama
    colorama.init()

    sockets = connect_sockets(args.address)

    abort_push = zmq.Context.instance().socket(zmq.PAIR)
    abort_push.bind('inproc://download_monitor/abort')
    abort_pull = zmq.Context.instance().socket(zmq.PAIR)
    abort_pull.connect('inproc://download_monitor/abort')

    def abort():
        abort_push.send('ABORT')

    command_rep = zmq.Context.instance().socket(zmq.REP)
    try:
        command_rep.bind('tcp://0.0.0.0:{}'.format(args.port))
    except:
        print("Can't bind to port {}".format(args.port))

    already_received = set()
    session = args.session[0]

    tasklist = load_tasklist(args.mission, session)
    print("Loaded {} tasks.".format(len(tasklist)))
    commandsDict = create_dictionary(tasklist)

    ui = MonitorUI(session, commandsDict, len(tasklist), abort)
    ui_thread = ui.run()
    ui.log("Loaded {} tasks.".format(len(tasklist)))

    with allow_interrupt(abort):
        while True:
            try:
                (read, _, _) = zmq.select(sockets + [abort_pull] + [command_rep], [], [])
            except KeyboardInterrupt:
                ui.log("Ending...")
                break

            if abort_pull in read:
                break

            if command_rep in read:
                handle_commands(command_rep.recv(), commandsDict, command_rep, ui)
                continue

            for ready in read:
                frame = ready.recv()
                frame = parse_frame(frame)
                process_frame(already_received, frame, commandsDict, ui)

    ui.stop()
    ui_thread.join()

run(parse_args())
