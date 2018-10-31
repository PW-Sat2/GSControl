from task import *

class Results:
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

        session_resources_names = Resources.session_names()
        for i in range(0, len(session_resources_names)):
            session_headers.insert(len(session_headers)-1, session_resources_names[i].replace(' ', '\n'))

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
        experiments_headers = [
            '#',
            'Name'
            # Place for utilized resources
        ]

        experiments_resources_names = Resources.scheduled_names()

        for i in range(0, len(experiments_resources_names)):
            experiments_headers.insert(len(experiments_headers), experiments_resources_names[i].replace(' ', '\n'))

        return experiments_headers


    @classmethod
    def scheduled_task(self, index, task_data):
        experiment_results = [
            index,
            task_data.name
            # Place for utilized resources
        ]

        experiment_resources_utilization = Resources.scheduled_params(task_data.resources_utilization)

        for i in range(0, len(experiment_resources_utilization)):
            experiment_results.insert(len(experiment_results), experiment_resources_utilization[i])

        return experiment_results
