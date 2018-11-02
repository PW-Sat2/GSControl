from tabulate import tabulate
from colorama import init, Fore, Style
from task_actions import *
from analyzer.resources import *
from analyzer.task import *
from analyzer.results import *
from analyzer.file import *
from analyzer.scheduled import *
from analyzer.commands import TelecommandDataFactory
from analyzer.state import State
from analyzer.limits import Limits

init()


class Analyzer:
    def __init__(self, tasks):
        self.tasks = tasks
        self.overall_resources_utilization = Resources.init_with_zeros()

    def run(self):
        session_results = [[]]
        scheduled_results = [[]]

        index = 1
        state = State()
        notes = Notes()
        limits = Limits()
        for task in self.tasks:
            task_data = TaskAnalyzer.process(task, state, limits)

            if task_data.is_scheduled:
                task_data.resources_utilization += Scheduled.process(task)
                scheduled_results.append(Results.scheduled_task(index,
                                                                task_data))

            session_results.append(Results.session_task(index,
                                                        task_data,
                                                        task_data.is_scheduled,
                                                        state.current_downlink_bitrate()))

            self.overall_resources_utilization += task_data.resources_utilization
            index += 1

        state.validate(notes)

        print '\n======================================= General =======================================\n'
        print '\n'.join(notes)
        
        print '\n======================== Resources utilization for THIS session ========================\n'
        print Style.RESET_ALL + tabulate(session_results, Results.session_headers())

        print '\nSession downlink frames count: {}'.format(self.overall_resources_utilization.session.downlink.frames_count)
        print 'Session downlink duration [s]: {}'.format(self.overall_resources_utilization.session.downlink.duration)
        print 'Session uplink frames count: {}'.format(self.overall_resources_utilization.session.uplink.frames_count)
        print 'Session uplink duration [s]: {}'.format(self.overall_resources_utilization.session.uplink.duration)
        print 'Session power budget energy [mWh]: {}'.format(self.overall_resources_utilization.session.power_budget.energy)
        print 'Session power budget mean power [mW]: {}'.format(self.overall_resources_utilization.session.power_budget.mean_power)

        print '\n================ Resources utilization for SCHEDULED experiments or tasks ================\n'
        if len(scheduled_results) > 1:
            print Style.RESET_ALL + tabulate(scheduled_results, Results.scheduled_headers())
            print '\nScheduled downlink frames count: {}'.format(self.overall_resources_utilization.scheduled.downlink.frames_count)
            print 'Scheduled downlink duration at 1200 2400 4800 9600 [s]: {}'.format(self.overall_resources_utilization.scheduled.downlink.duration)
            print 'Scheduled power budget energy at 1200 2400 4800 9600 [mWh]: {}'.format(self.overall_resources_utilization.scheduled.power_budget.energy)
            print 'Scheduled power budget mean power at 1200 2400 4800 9600 [mW]: {}'.format(self.overall_resources_utilization.scheduled.power_budget.mean_power)
            print 'Scheduled tasks duration [s]: {}'.format(self.overall_resources_utilization.scheduled.task_duration)
            print 'Scheduled storage usage [kB]: {}'.format(self.overall_resources_utilization.scheduled.storage)
        else:
            print Fore.CYAN + '[Info] No scheduled experiments or tasks.' + Style.RESET_ALL


if __name__ == '__main__':
    import os
    import sys
    import argparse

    sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    import telecommand as tc
    import datetime
    from devices import camera

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True,
	                    help="Path to *.py file with session tasks (tasks = [...]). Examples in test_sessions dir.")
    args = vars(parser.parse_args())

    if not File.valid(args["file"]):
        raise SyntaxError('File: {} has a wrong syntax. This file should contain a tasks = [...] list only with session tasks. Examples in test_sessions dir.'.format(args["file"]))

    with open(args["file"]) as tasks_file:
        exec(tasks_file)
        tasks_file.close()

    analyzer = Analyzer(tasks)
    analyzer.run()
