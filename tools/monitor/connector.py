import zmq
import json
import traceback
from time import sleep

from telecommand.fs import DownloadFile   
from radio.task_actions import Send, SendLoop, WaitMode
import telecommand as tc
from model import DownloadFileTask

class MonitorConnector:
    def __init__(self, host="localhost", port=7007, socket_timeout=500):
        self.working = False
        self.socket_timeout = socket_timeout
        self.socket = zmq.Context.instance().socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, self.socket_timeout)
        self.host = host
        self.port = port

    def _internal_connect(self):
        try:
            self.socket.connect('tcp://{}:{}'.format(self.host, self.port))
            self.working = True
            return True
        except:
            print("Sorry, don't work")
            self.working = False
            traceback.print_exc()
            return False

    def connect(self):
        if self.socket is None:
            return self._reconnect()
        else:
            return self._internal_connect()

    def _disconnect(self):
        self.socket.close()
        self.socket = None
        self.working = False

    def _reconnect(self):
        self.socket = zmq.Context.instance().socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, self.socket_timeout)
        result = self._internal_connect()
        sleep(0.2)
        return result

    def _send_command_with_receive(self, command):
        if not self.working:
            print("Reconnecting...") 
            if not self._reconnect():
                return None 
            
        try:
            self.socket.send(json.dumps(command))    
            data = self.socket.recv()
        except zmq.Again:
            print("Not connected. ") 
            self._disconnect()
            return None
        except zmq.ZMQError:
            print("ZMQError. ") 
            self._disconnect()
            traceback.print_exc()
            return None

        return data

    def get_missings_for_command(self, telecommand): 
        if not isinstance(telecommand, DownloadFile):
            print("Sorry, only for DownloadFile")
            return None

        command = {
            "command" : "GetMissingsForOneTask",
            "data" : telecommand.correlation_id()
        }
        data = self._send_command_with_receive(command)   
        if data is None:
            return None
        if data == "":
            return data

        newTask = json.loads(data, object_hook=DownloadFileTask.from_dict)
        newCommand = DownloadFile(newTask.correlation_id, newTask.path, newTask.chunks)
        return newCommand

    def get_additional_tasks(self):
        command = { "command" : "GetTasklistWithAllMissings" }
        data = self._send_command_with_receive(command)
        if not data:
            return None

        newItems = json.loads(data, object_hook=DownloadFileTask.from_dict)
        newTasks = []
        for newItem in newItems:
            newCommand = DownloadFile(newItem.correlation_id, newItem.path, newItem.chunks) 
            newTasks.append([newCommand, Send, WaitMode.Wait])
        newTasks.append([[tc.SendBeacon(), 20], SendLoop, WaitMode.NoWait])
        return newTasks