from task import *
from resources import *
from experiments.payload_commissioning import *
import telecommand as tc

class PerformPayloadCommissioningExperiment:
    @classmethod
    def process(self, resources_utilization):
        resources_utilization.scheduled.task_duration = PayloadCommissioning.task_duration()
        resources_utilization.scheduled.storage = PayloadCommissioning.storage_usage()
        resources_utilization.scheduled.power_budget.energy = PayloadCommissioning.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = PayloadCommissioning.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = PayloadCommissioning.downlink_durations()
        return resources_utilization

class ScheduledTaskDataFactory(object):
    map = dict({
        tc.PerformPayloadCommissioningExperiment: PerformPayloadCommissioningExperiment
    })

    def get_process(self, task):
        taskType = type(task)
        if taskType in ScheduledTaskDataFactory.map:
            return ScheduledTaskDataFactory.map[taskType]
        return None

class Scheduled(object):
    @classmethod
    def process(self, task):
        resources_utilization = Resources.init_with_zeros()

        scheduledProcess = ScheduledTaskDataFactory().get_process(task)
        if not scheduledProcess is None:
            scheduledProcess.process(resources_utilization)
        return resources_utilization
