from task import *


class Results:
    '''Prepares results ready to display.

    Output can be displayed as a table directly.
    It returns both tables content and headers.
    '''

    @classmethod
    def session_headers(self):
        session_headers = [
            '#',
            'Name',
            'Is\nscheduled?',
            'Current\nbitrate\n[bps]',
            # Place for utilized resources
            'Notes'
        ]

        session_names = Resources.session_names()
        for i in range(0, len(session_names)):
            session_headers.insert(len(session_headers)-1, 
                                   session_names[i].replace(' ', '\n'))

        return session_headers

    @classmethod
    def session_task(self, index, task_data, is_experiment, bitrate_index):
        task_results = []

        task_results = [
            index,
            task_data.name,
            is_experiment,
            TaskAnalyzer.to_bitrate(task_data.bitrate_index),
            # Place for utilized resources
            '\n'.join(task_data.notes)
        ]

        task_resources_utilization = Resources.session_params(task_data.resources_utilization)
    
        for i in range(0, len(task_resources_utilization)):
            task_results.insert(len(task_results)-1, task_resources_utilization[i])

        return task_results
    
    @classmethod
    def scheduled_headers(self):
        scheduled_headers = [
            '#',
            'Name'
            # Place for utilized resources
        ]

        scheduled_names = Resources.scheduled_names()

        for i in range(0, len(scheduled_names)):
            scheduled_headers.insert(len(scheduled_headers),
                                     scheduled_names[i])

        return scheduled_headers

    @classmethod
    def scheduled_task(self, index, task_data):
        scheduled_results = [
            index,
            task_data.name
            # Place for utilized resources
        ]

        scheduled_utilization = Resources.scheduled_params(task_data.resources_utilization)

        for i in range(0, len(scheduled_utilization)):
            scheduled_results.insert(len(scheduled_results),
                                     scheduled_utilization[i])

        return scheduled_results
