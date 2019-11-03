from collections import OrderedDict
from telecommand.fs import DownloadFile   
from response_frames.common import FileSendSuccessFrame, FileSendErrorFrame 

class MonitorLive():
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
        """
        Receives all incoming frames and decodes them.
        Use Ctrl+C to break the loop.
        Captured frames are returned from this function
        """
        import pprint
        import datetime

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

                timestamp_str = '\x1b[36m{}\x1b[0m'.format(datetime.datetime.now().time().strftime('%H:%M:%S'))
                counter_str = '\x1b[90m{:3d}\x1b[0m'.format(counter)
                print("{} {} {}".format(timestamp_str, counter_str, pprint.pformat(x)))
                counter += 1
        except KeyboardInterrupt:
            pass
        finally:
            newTaskList = self._generateNewTasklist(commandsDict)
            print("Generating {} new tasks.".format(len(newTaskList)))
            return newTaskList
