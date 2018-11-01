from task import *
from resources import *
from experiments.payload_commissioning import *

class Scheduled:
    @classmethod
    def process(self, task):
        resources_utilization = Resources.init_with_zeros()

        if TaskAnalyzer.get_task_name(task) == "PerformPayloadCommissioningExperiment":
            return PerformPayloadCommissioningExperiment.process(resources_utilization)

        return resources_utilization


class PerformPayloadCommissioningExperiment:
    @classmethod
    def process(self, resources_utilization):
        resources_utilization.scheduled.task_duration = PayloadCommissioning.task_duration()
        resources_utilization.scheduled.storage = PayloadCommissioning.storage_usage()
        resources_utilization.scheduled.power_budget.energy = PayloadCommissioning.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = PayloadCommissioning.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = PayloadCommissioning.downlink_durations()
        return resources_utilization
