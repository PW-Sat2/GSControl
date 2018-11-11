from task import *
from resources import *
from scheduled_tasks.payload_commissioning import *
from scheduled_tasks.camera_commissioning import *
from scheduled_tasks.radfet import *
from scheduled_tasks.suns import *
from scheduled_tasks.sads import *
from scheduled_tasks.sail import *
from scheduled_tasks.adcs import *
from scheduled_tasks.photo_tc import *
import telecommand as tc
from commands import TelecommandDataFactory

class PerformSunSExperiment:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        suns_experiment = SunsExperiment(frame_payload)

        resources_utilization.scheduled.task_duration = suns_experiment.task_duration()
        resources_utilization.scheduled.storage = suns_experiment.storage_usage()
        resources_utilization.scheduled.power_budget.energy = suns_experiment.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = suns_experiment.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = suns_experiment.downlink_durations()
        return resources_utilization


class PerformRadFETExperiment:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        redfet_experiment = RadfetExperiment(frame_payload)

        resources_utilization.scheduled.task_duration = redfet_experiment.task_duration()
        resources_utilization.scheduled.storage = redfet_experiment.storage_usage()
        resources_utilization.scheduled.power_budget.energy = redfet_experiment.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = redfet_experiment.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = redfet_experiment.downlink_durations()
        return resources_utilization


class PerformSailExperiment:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        sail_experiment = SailExperiment()

        resources_utilization.scheduled.task_duration = sail_experiment.task_duration()
        resources_utilization.scheduled.storage = sail_experiment.storage_usage()
        resources_utilization.scheduled.power_budget.energy = sail_experiment.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = sail_experiment.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = sail_experiment.downlink_durations()
        return resources_utilization


class PerformPayloadCommissioningExperiment:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        resources_utilization.scheduled.task_duration = PayloadCommissioning.task_duration()
        resources_utilization.scheduled.storage = PayloadCommissioning.storage_usage()
        resources_utilization.scheduled.power_budget.energy = PayloadCommissioning.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = PayloadCommissioning.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = PayloadCommissioning.downlink_durations()
        return resources_utilization


class PerformSADSExperiment:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        sads_experiment = SadsExperiment()

        resources_utilization.scheduled.task_duration = sads_experiment.task_duration()
        resources_utilization.scheduled.storage = sads_experiment.storage_usage()
        resources_utilization.scheduled.power_budget.energy = sads_experiment.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = sads_experiment.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = sads_experiment.downlink_durations()
        return resources_utilization


class PerformCameraCommissioningExperiment:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        resources_utilization.scheduled.task_duration = CameraCommissioning.task_duration()
        resources_utilization.scheduled.storage = CameraCommissioning.storage_usage()
        resources_utilization.scheduled.power_budget.energy = CameraCommissioning.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = CameraCommissioning.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = CameraCommissioning.downlink_durations()
        return resources_utilization


class PerformCopyBootSlotsExperiment:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        return resources_utilization


class TakePhotoTelecommand:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        take_photo = TakePhoto(frame_payload)

        resources_utilization.scheduled.task_duration = take_photo.task_duration()
        resources_utilization.scheduled.storage = take_photo.storage_usage()
        resources_utilization.scheduled.power_budget.energy = take_photo.energy_consumptions()
        resources_utilization.scheduled.downlink.frames_count = take_photo.downlink_frames_count()
        resources_utilization.scheduled.downlink.duration = take_photo.downlink_durations()
        return resources_utilization


class SetAdcsModeTelecommand:
    @classmethod
    def process(self, frame_payload):
        resources_utilization = Resources.init_with_zeros()
        set_adcs_mode = SetAdcsMode(frame_payload)

        resources_utilization.scheduled.task_duration = set_adcs_mode.task_duration()
        resources_utilization.scheduled.power_budget.mean_power = set_adcs_mode.mean_powers()
        return resources_utilization


class ScheduledTaskDataFactory(object):
    map = dict({
        tc.PerformSunSExperiment:                 PerformSunSExperiment,
        tc.PerformRadFETExperiment:               PerformRadFETExperiment,
        tc.PerformPayloadCommissioningExperiment: PerformPayloadCommissioningExperiment,
        tc.PerformCameraCommissioningExperiment:  PerformCameraCommissioningExperiment,
        tc.TakePhotoTelecommand:                  TakePhotoTelecommand,
        tc.PerformSADSExperiment:                 PerformSADSExperiment,
        tc.PerformSailExperiment:                 PerformSailExperiment,
        tc.SetAdcsModeTelecommand:                SetAdcsModeTelecommand
    })

    def get_process(self, task):
        task_type = type(task[0])
        if task_type in ScheduledTaskDataFactory.map:
            return ScheduledTaskDataFactory.map[task_type]
        return None


class Scheduled(object):
    '''
    Processes scheduled tasks and returns scheduled resources utilization.
    '''
    @classmethod
    def process(self, task):
        resources_utilization = Resources.init_with_zeros()

        scheduled_process = ScheduledTaskDataFactory().get_process(task)
        if not scheduled_process is None:
            resources_utilization = scheduled_process.process(self.get_frame_payload(task))
        return resources_utilization

    @classmethod
    def get_frame_payload(self, task):
        frame = task[0]
        self.telecommand_data_factory = TelecommandDataFactory()
        command_data = self.telecommand_data_factory.get_telecommand_data(frame)
        return command_data.get_payload()
