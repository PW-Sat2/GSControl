
import sys
import os
from collections import OrderedDict

sys.path.append(os.path.join(os.path.dirname(__file__),
                '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__),
                '../..'))

from telecommand.fs import DownloadFile   
from response_frames.common import FileSendSuccessFrame, FileSendErrorFrame 
from radio.task_actions import Send, SendLoop, WaitMode
import telecommand as tc

import zmq
import json

class Monitor():
    def __init__(self, recv, frame_decoder):
        self.receiver = recv
        self.frame_decoder = frame_decoder

    def run(self, tasks):

        download_commands = []

        for item in tasks:
            command = item[0]
            if isinstance(command, DownloadFile):
                download_commands.append(command)

        
        return self.receiver_loop(download_commands)

    def _createDictionary(self, commands):
        commandsDict = OrderedDict()

        for command in commands:
            commandsDict[command._correlation_id] = command

        return commandsDict

    def _generateNewTasklist(self, commandsDict):
        newTasks = []
        for _, command in commandsDict.items():
            newTasks.append(command)

        return newTasks

    def receiver_loop(self, commands):
        import datetime
        """
        Receives all incoming frames and decodes them.
        Use Ctrl+C to break the loop.
        Captured frames are returned from this function
        """
        import pprint
        frames = []

        commandsDict = self._createDictionary(commands)

        try:
            counter = 0
            print 'Monitoring for download....'
            while True:
                data = self.receiver.decode_kiss(self.receiver.receive())
                x = self.frame_decoder.decode(data)
                if not isinstance(x, FileSendSuccessFrame) and not isinstance(x, FileSendErrorFrame):
                    continue

                try:
                    tasklistCommandChunks = commandsDict[x.correlation_id]._seqs
                    if x._seq in tasklistCommandChunks:
                        tasklistCommandChunks.remove(x._seq)
                    if len(tasklistCommandChunks) == 0:
                        del commandsDict[x.correlation_id]
                except KeyError:
                    pass    
                # x.correlation_id,  x._seq

                timestamp_str = '\x1b[36m{}\x1b[0m'.format(datetime.datetime.now().time().strftime('%H:%M:%S'))
                counter_str = '\x1b[90m{:3d}\x1b[0m'.format(counter)
                print("{} {} {}".format(timestamp_str, counter_str, pprint.pformat(x)))
                counter += 1
                # frames.append(x)

                if counter == 356:
                    break

        except KeyboardInterrupt:
            pass
        finally:
            newTaskList = self._generateNewTasklist(commandsDict)
            print("Generating {} new tasks.".format(len(newTaskList)))
            return newTaskList
        #     return frames

        i = 0

class MonitorConnector:
    def __init__(self):
        self.working = False
        self.socket = zmq.Context.instance().socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.port = 7007

        try:
            self.socket.connect('tcp://127.0.0.1:{}'.format(self.port))
            self.working = True
        except:
            print("Sorry, don't work")

    def get_missings_for_command(self, telecommand):
        if not self.working:
            print("Sorry, don't work")      
            return None     

        if not isinstance(telecommand, DownloadFile):
            print("Sorry, only for DownloadFile")
            return None

        try:
            self.socket.send(json.dumps(['M', telecommand.correlation_id()]))    
            data = self.socket.recv()
        except zmq.Again:
            return None
        except zmq.ZMQError:
            self.working = False
            return None

        if not data:
            return None

        newTask = json.loads(data)
        newCommand = DownloadFile(newTask["_correlation_id"], str(newTask["_path"]), newTask["_seqs"])     
        return newCommand

    def get_additional_tasks(self):
        if not self.working:
            print("Sorry, don't work. ")      
            return None     

        try:
            self.socket.send(json.dumps(['T']))    
            data = self.socket.recv()
        except zmq.Again:
            print("Not connected. ") 
            return None
        except zmq.ZMQError:
            print("ZMQError. ") 
            self.working = False
            return None

        if not data:
            return None

        newItems = json.loads(data)
        newTasks = []
        for newItem in newItems:
            newCommand = DownloadFile(newItem["_correlation_id"], str(newItem["_path"]), newItem["_seqs"]) 
            newTasks.append([newCommand, Send, WaitMode.Wait])
        newTasks.append([[tc.SendBeacon(), 20], SendLoop, WaitMode.NoWait])
        return newTasks