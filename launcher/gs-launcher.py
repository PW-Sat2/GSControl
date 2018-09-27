#!/usr/bin/python

import subprocess
from time import sleep
from threading import Thread

from config import config

class ProcessData:
        def __init__(self):
            self.process = None
            self.command = None
            self.args = None
            self.kwargs = None
            self.isWatched = True

class Executor:
    def __init__(self):
        self.isEnabled = True
        self.processes = []

    def _echo_command(self,command):
        if not isinstance(command, basestring):
            print(' '.join(command))
        else: 
            print(command)

    def execWait(self,command, *args, **kwargs):
        self._echo_command(command)
        subprocess.call(command, *args, **kwargs)

    def _execNoWaitSetWatch(self,command, isWatching, *args, **kwargs):
        self._echo_command(command)

        process = ProcessData()
        process.command = command
        process.args = args
        process.kwargs = kwargs
        process.isWatched = isWatching

        process.process = subprocess.Popen(command, *args, **kwargs)
        self.processes.append(process)
        return process

    def execNoWait(self,command, *args, **kwargs):
        return self._execNoWaitSetWatch(command, True, *args, **kwargs)

    def execNoWaitNoWatch(self,command, *args, **kwargs):
        return self._execNoWaitSetWatch(command, False, *args, **kwargs)

    def startWatchdog(self):
        watchdogThread = Thread(target = self._watchdog)
        watchdogThread.start()

    def _watchdog(self):
        while self.isEnabled:
            sleep(2.0)
            for process in self.processes:
                returnCode = process.process.poll()
                print returnCode
                if returnCode is not None and process.isWatched:
                    self._restartProcess(process)

    def _restartProcess(self, oldProcessData):
        self.processes.remove(oldProcessData)

        process = ProcessData()
        process.command = oldProcessData.command
        process.args = oldProcessData.args
        process.kwargs = oldProcessData.kwargs
        process.process = subprocess.Popen(oldProcessData.command, *oldProcessData.args, **oldProcessData.kwargs)

        self.processes.append(process)

    def killEmAll(self):
        self.isEnabled = False
        for process in self.processes:   
            process.process.terminate()     

    
def start_gnuradio(executor):
    executor.execNoWait(['{0}/start_gnuradio.sh {1} {2}'.format(config.gs_launcher_script_relative_path, config.base_path, config.gnu_radio_folder)], shell=True)

def start_rotctld(executor):
    #executor.execNoWait(['x-terminal-emulator', '-e', '/usr/bin/rotctld', '-m 901 -r /dev/rotor'])
    executor.execNoWait(['/usr/bin/rotctld', '-m 901 -r /dev/rotor'])

def start_rigctld(executor):
    #executor.execNoWait(['x-terminal-emulator', '-e', '/usr/bin/rigctld', '-m 214 -r /dev/radio -s 9600'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    executor.execNoWait(['/usr/bin/rigctld', '-m 214 -r /dev/radio -s 9600'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def start_gpredict(executor):
    executor.execNoWait('gpredict')

def start_satellite_terminal(executor):
    executor.execNoWaitNoWatch(['x-terminal-emulator', '-e', 
        '/usr/bin/python', 
        #'{0}{1}'.format(config.base_path, config.gscontrol_main_path),
        #'-c',
        #'{0}{1}'.format(config.base_path, config.gscontrol_config_path) 
        ]) 

def start_satellite_receiver(executor):
    start_satellite_terminal(executor)
    
def main():
    executor = Executor()

    start_gnuradio(executor)
    #start_rotctld(executor)
    #start_rigctld(executor)
    #start_gpredict(executor)
    #start_satellite_terminal(executor)
    #start_satellite_receiver(executor)

    executor.startWatchdog()

    sleep(60.0)
    executor.killEmAll()

if __name__ == "__main__":
    main()