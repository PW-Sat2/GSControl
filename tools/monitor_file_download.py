import argparse
import os
import sys
import datetime
import pprint

#from termgraph import termgraph as tg

from colorama import Fore, Style, Back
import zmq
from zmq.utils.win32 import allow_interrupt
from collections import OrderedDict

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import response_frames
from utils import ensure_byte_list, ensure_string
from telecommand.fs import DownloadFile  

Decoder = response_frames.FrameDecoder(response_frames.frame_factories)

last_cid = 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('session', nargs=1, help='Session number')
    parser.add_argument('address', nargs='+', help='Address to connect for frames')
    parser.add_argument('--port', '-p', help='Command port', type=int, default=7007)

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

def load_tasklist(session):
    tasks_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'mission', 'sessions', str(session), 'tasklist.py')  
 
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

def print_results(commandsDict):
    pass
    # labels = [x._path for x in commandsDict.itervalues()]
    # data = [len(x._seqs) for x in commandsDict.itervalues()]

    # print("*" * 40)
    # for i in range(0, len(labels)):
    #     print("{}\t\t{}".format(labels[i], data[i]))


    # labels = ['2007', '2008', '2009', '2010', '2011', '2012', '2014']
    # data = [[183.32, 190.52], [231.23, 5.0], [16.43, 53.1], [50.21, 7.0], [508.97, 10.45], [212.05, 20.2], [30.0, 20.0]]
    # normal_data = [[48.059508408796894, 50.0], [60.971862871927556, 0.0],
    #             [3.080530401034929, 12.963561880120743],
    #             [12.184670116429496, 0.5390254420008624],
    #             [135.82632600258734, 1.4688443294523499],
    #             [55.802608883139285, 4.096593359206555],
    #             [6.737818025010781, 4.042690815006468]]
    # len_categories = 2
    # args = {'filename': 'data/ex4.dat', 'title': None, 'width': 50,
    #         'format': '{:<5.2f}', 'suffix': '', 'no_labels': True,
    #         'color': None, 'vertical': False, 'stacked': True,
    #         'different_scale': False, 'calendar': False,
    #         'start_dt': None, 'custom_tick': '', 'delim': '',
    #         'verbose': False, 'version': False}
    # colors = [91, 94]
    # tg.chart(None, data, None, labels)


def process_frame(already_received, frame, commandsDict):
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

    timestamp_str = '\x1b[36m{}\x1b[0m'.format(datetime.datetime.now().time().strftime('%H:%M:%S'))
    print("{} {}".format(timestamp_str, pprint.pformat(frame)))

    print_results(commandsDict)

    # if frame.correlation_id != last_cid:
    #     already_received.clear()
    #     last_cid = frame.correlation_id
    #     print("\n\n====================================")
    #     print("Correlation id: {0}".format(frame.correlation_id))
    #     print("====================================\n")

    # if frame.seq() in already_received:
    #     return

    # file_list = RemoteFileTools.parse_file_list(frame)

    # for f in file_list:
    #     print("{0}:\t{1}".format(f['File'], f['Chunks']))

    # already_received.add(frame.seq())


def run(args):
    import colorama
    colorama.init()

    sockets = connect_sockets(args.address)

    abort_push = zmq.Context.instance().socket(zmq.PAIR)
    abort_push.bind('inproc://download_monitor/abort')
    abort_pull = zmq.Context.instance().socket(zmq.PAIR)
    abort_pull.connect('inproc://download_monitor/abort')

    command_rep = zmq.Context.instance().socket(zmq.REP)
    try:
        command_rep.bind('tcp://0.0.0.0:{}'.format(args.port))
    except:
        print("Can't bind to port {}".format(args.port))

    already_received = set()

    tasklist = load_tasklist(args.session[0])
    print("Loaded {} tasks.".format(len(tasklist)))
    commandsDict = create_dictionary(tasklist)

    def abort():
        abort_push.send('ABORT')

    with allow_interrupt(abort):
        while True:
            (read, _, _) = zmq.select(sockets + [abort_pull] + [command_rep], [], [])

            if abort_pull is read:
                break

            if command_rep is read:
                pass

            for ready in read:
                frame = ready.recv()
                frame = parse_frame(frame)
                process_frame(already_received, frame, commandsDict)


run(parse_args())
