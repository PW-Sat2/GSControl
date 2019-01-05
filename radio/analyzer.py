from tabulate import tabulate
from colorama import init, Fore, Style
from analyzer_engine.resources import *
from analyzer_engine.task import *
from analyzer_engine.results import *
from analyzer_engine.file import *
from analyzer_engine.scheduled import *
from analyzer_engine.commands import TelecommandDataFactory
from analyzer_engine.state import State
from analyzer_engine.limits import Limits

init()


class Analyzer:
    def run(self, tasks):
        session_results = [[]]
        scheduled_results = [[]]
        overall_resources_utilization = Resources.init_with_zeros()

        index = 1
        state = State()
        notes = Notes()
        limits = Limits()
        analyzer = TaskAnalyzer()
        for task in tasks:
            task_data = analyzer.process(task, state, limits)

            if task_data.is_scheduled:
                task_data.resources_utilization += Scheduled.process(task)
                scheduled_results.append(Results.scheduled_task(index,
                                                                task_data))

            session_results.append(Results.session_task(index,
                                                        task_data,
                                                        task_data.is_scheduled,
                                                        state.current_downlink_bitrate()))

            overall_resources_utilization += task_data.resources_utilization
            index += 1

        state.validate(notes)

        print '\n======================================= General =======================================\n'
        print '\n'.join(notes)
        
        print '\n======================== Resources utilization for THIS session ========================\n'
        print Style.RESET_ALL + tabulate(session_results, Results.session_headers())

        print '\nSession downlink frames count: {}'.format(overall_resources_utilization.session.downlink.frames_count)
        print 'Session downlink duration [s]: {}'.format(overall_resources_utilization.session.downlink.duration)
        print 'Session uplink frames count: {}'.format(overall_resources_utilization.session.uplink.frames_count)
        print 'Session uplink duration [s]: {}'.format(overall_resources_utilization.session.uplink.duration)
        print 'Session power budget energy [mWh]: {}'.format(overall_resources_utilization.session.power_budget.energy)
        print 'Session power budget mean power [mW]: {}'.format(overall_resources_utilization.session.power_budget.mean_power)

        print '\n================ Resources utilization for SCHEDULED experiments or tasks ================\n'
        if len(scheduled_results) > 1:
            print Style.RESET_ALL + tabulate(scheduled_results, Results.scheduled_headers())
            print '\nScheduled downlink frames count: {}'.format(overall_resources_utilization.scheduled.downlink.frames_count)
            print 'Scheduled downlink duration at 1200 2400 4800 9600 [s]: {}'.format(overall_resources_utilization.scheduled.downlink.duration)
            print 'Scheduled power budget energy at 1200 2400 4800 9600 [mWh]: {}'.format(overall_resources_utilization.scheduled.power_budget.energy)
            print 'Scheduled power budget mean power at 1200 2400 4800 9600 [mW]: {}'.format(overall_resources_utilization.scheduled.power_budget.mean_power)
            print 'Scheduled tasks duration [s]: {}'.format(overall_resources_utilization.scheduled.task_duration)
            print 'Scheduled storage usage [kB]: {}'.format(overall_resources_utilization.scheduled.storage)
        else:
            print Fore.CYAN + '[Info] No scheduled experiments or tasks.' + Style.RESET_ALL


    def load(self, tasks_file_path):
        import os
        import sys
        

        sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
        import telecommand as tc
        import datetime
        from radio.task_actions import *
        from devices import camera
        from devices.adcs import AdcsMode
        from devices.camera import CameraLocation, PhotoResolution
        from devices.comm import BaudRate
        
        if not os.path.exists(tasks_file_path):
            return []

        if not File.valid(tasks_file_path):
            raise SyntaxError('File: {} has a wrong syntax. This file should contain a tasks = [...] list only with session tasks. Examples in test_sessions dir.'.format(tasks_file_path))

        with open(tasks_file_path) as tasks_file:
            exec(tasks_file)
            tasks_file.close()

        return tasks

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True,
	                    help="Path to *.py file with session tasks (tasks = [...]). Examples in test_sessions dir.")
    args = vars(parser.parse_args())

    analyzer = Analyzer()
    analyzer.run(analyzer.load(args["file"]))
