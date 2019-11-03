import sys
import os
import zmq
import json

# sys.path.append(os.path.join(os.path.dirname(__file__),
#                 '../../PWSat2OBC/integration_tests'))
# sys.path.append(os.path.join(os.path.dirname(__file__),
#                 '../..'))

from telecommand.fs import DownloadFile   
from radio.task_actions import Send, SendLoop, WaitMode
import telecommand as tc

class MonitorConnector:
    def __init__(self, host="tcp://127.0.0.1", port=7007):
        self.working = False
        self.socket = zmq.Context.instance().socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)

        try:
            self.socket.connect('{}:{}'.format(host, port))
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
            command = {
                "command" : "GetMissingsForOneTask",
                "data" : telecommand.correlation_id()
            }
            self.socket.send(json.dumps(command))    
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
            command = { "command" : "GetTasklistWithAllMissings" }
            self.socket.send(json.dumps(command))    
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