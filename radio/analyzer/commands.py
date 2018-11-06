import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),
                '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__),
                '../..'))

import math
import telecommand as tc
from resources import *
from subsystems import *
from task_actions import *

class TelecommandData(object):
    uplink_header_bytes_count = 3
    downlink_header_bytes_count = 3
    downlink_frame_bytes_count = 235

    def __init__(self, telecommand):
        self.telecommand = telecommand
        self.correlation_id = None

    def telecommand_name(self):
        return type(self.telecommand).__name__

    def get_payload(self):
        return self.telecommand.payload()

    def get_payload_size(self):
        payload = self.get_payload()
        return len(payload)

    def get_uplink_duration(self, bitrate):
        return Comm.uplink_bytes_duration(self.uplink_header_bytes_count +
                                          self.get_payload_size(), bitrate)

    def get_uplink_frames_count(self):
        return 1

    def get_downlink_duration(self, bitrate):
        return Comm.downlink_bytes_duration(self.downlink_header_bytes_count +
                                            self.get_response_bytes_count(),
                                            bitrate)
    
    def get_downlink_energy_consumption(self, duration):
        return Comm.downlink_energy_consumption(duration)

    def get_downlink_frames_count(self):
        response_bytes_count = self.get_response_bytes_count()
        bytes_count = self.downlink_header_bytes_count + response_bytes_count
        return int(math.ceil(bytes_count / self.downlink_frame_bytes_count))

    def get_correlation_id(self):
        return self.correlation_id

    def get_response_bytes_count(self):
        raise NotImplementedError()

    def get_requires_wait(self):
        raise NotImplementedError()

    def get_requires_send_receive(self):
        raise NotImplementedError()

    def get_extra_notes(self):
        return []

    def is_scheduled(self):
        return False

    def check_frame_size(self, notes, limits):
        payload_size = self.get_payload_size()
        if payload_size > self.telecommand.MAX_PAYLOAD_SIZE:
            notes.error('Frame is too long: {0}'.format(payload_size))

    def process_common_command(self, state, notes, send_mode, wait_mode, limits):
        state.add_corelation_id(self.get_correlation_id(), notes)
        self.check_frame_size(notes, limits)       

        for extra_note in self.get_extra_notes():
            notes.info(extra_note)

        if self.get_requires_send_receive() and send_mode != SendReceive:
            notes.warning('SendReceive suggested')

        if self.get_requires_wait() and wait_mode != WaitMode.Wait:
            notes.warning('Wait suggested')

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)

class SimpleTelecommandData(TelecommandData):
    def __init__(self, telecommand, response_bytes_count):
        super(SimpleTelecommandData, self).__init__(telecommand)
        self.response_bytes_count = response_bytes_count

    def get_response_bytes_count(self):
        return self.response_bytes_count

    def get_requires_wait(self):
        return False

    def get_requires_send_receive(self):
        return False

def set_correlation_id(init):
    def wrap(self, telecommand, *args, **kwargs):
        init(self, telecommand, *args, **kwargs)
        self.correlation_id = telecommand.correlation_id()
    return wrap

class SetBuiltinDetumblingBlockMaskTelecommandData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetBuiltinDetumblingBlockMaskTelecommandData, self).__init__(telecommand, 2)

class SetAdcsModeTelecommandData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetAdcsModeTelecommandData, self).__init__(telecommand, 2)

class SetAntennaDeploymentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetAntennaDeploymentData, self).__init__(telecommand, 2)

class SetBootSlotsData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetBootSlotsData, self).__init__(telecommand, 4)

class EnterIdleStateData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(EnterIdleStateData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.info('Prefer using Ping/SendBeacon telecommands instead')
        if self.telecommand._duration > 100:
            notes.warning('Prolonged COMM Idle state with significant power consumption (>= 100mWh)')

class SendBeaconData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SendBeaconData, self).__init__(telecommand, 1)

    def get_correlation_id(self):
        return None

class ResetTransmitterTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(ResetTransmitterTelecommandData, self).__init__(telecommand, 2)

    def get_correlation_id(self):
        return None

    def get_extra_notes(self):
        return ['Wait 2-3 seconds before sending next command']

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        state.reset_transmitter()

class SetBitrateData(SimpleTelecommandData):
    BIT_RATE_MAP = [0, 1200, 2400, 0, 4800, 0, 0, 0, 9600]
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetBitrateData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        payload = self.get_payload()
        index = payload[1]
        if index not in [1, 2, 4, 8]:
            notes.error('Wrong bitrate value: {0}'.format(index))
        else:
            state.change_downlink_bit_rate(SetBitrateData.BIT_RATE_MAP[index])

class GetCompileInfoTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(GetCompileInfoTelecommandData, self).__init__(telecommand, 300)

class DisableOverheatSubmodeData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(DisableOverheatSubmodeData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning('Overheat submode can be enabled only by restarting EPS controller')
        notes.warning('It is not possible to determine current state of overheat submode (enabled/disabled)')
        if self.telecommand._controller != 0 and self.telecommand._controller != 1:
            notes.error('Invalid controller id: "{0}"'.format(self.telecommand._controller))

class PerformDetumblingExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformDetumblingExperimentData, self).__init__(telecommand, 2)

class AbortExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(AbortExperimentData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning('Aborting experiment has unpredicted results')
        notes.warning('Experiment is aborted during next experiment loop iteration')

class PerformSunSExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformSunSExperimentData, self).__init__(telecommand, 2)

class PerformRadFETExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformRadFETExperimentData, self).__init__(telecommand, 2)

class PerformSailExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformSailExperimentData, self).__init__(telecommand, 2)

class PerformPayloadCommissioningExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformPayloadCommissioningExperimentData, self).__init__(telecommand, 2)

    def is_scheduled(self):
        return True

class PerformSADSExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformSADSExperimentData, self).__init__(telecommand, 2)

class PerformCameraCommissioningExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformCameraCommissioningExperimentData, self).__init__(telecommand, 2)

class CopyBootSlotsData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(CopyBootSlotsData, self).__init__(telecommand, 2)

class SetErrorCounterConfigData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetErrorCounterConfigData, self).__init__(telecommand, 2)

class GetErrorCounterConfigData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(GetErrorCounterConfigData, self).__init__(telecommand, 4)

    def get_correlation_id(self):
        return None

class DownloadFileData(TelecommandData):
    MAX_PATH_LENGTH = 100
    @set_correlation_id
    def __init__(self, telecommand):
        super(DownloadFileData, self).__init__(telecommand)

    def get_response_bytes_count(self):
        payload = self.get_payload()
        path_length = payload[1]
        seqs = payload[(path_length + 3):]
        seqs_count = len(seqs) / 4
        return seqs_count * self.downlink_frame_bytes_count

    def get_requires_wait(self):
        return True

    def get_requires_send_receive(self):
        return False

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        path = self.telecommand._path
        if len(path) > self.MAX_PATH_LENGTH:
            notes.error('Path too long: {0}'.format(len(path)))
        seqs = self.telecommand._seqs
        if len(seqs) > limits.max_response_frames():
            notes.error('Too many sequences are requested for download: {0}'.format(len(seqs)))
        
class RemoveFileData(TelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(RemoveFileData, self).__init__(telecommand)

    def get_response_bytes_count(self):
        payload = self.get_payload()
        path_length = payload[1]
        return 2 + path_length

    def get_requires_wait(self):
        return False

    def get_requires_send_receive(self):
        return False

class ListFilesData(TelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(ListFilesData, self).__init__(telecommand)

    def get_response_bytes_count(self):
        return 5 * self.downlink_frame_bytes_count # big unknown

    def get_requires_wait(self):
        return False

    def get_requires_send_receive(self):
        return False

class EraseFlashData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(EraseFlashData, self).__init__(telecommand, 3)

class RawI2CData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(RawI2CData, self).__init__(telecommand, self.downlink_frame_bytes_count)

class ReadMemoryData(TelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(ReadMemoryData, self).__init__(telecommand)

    def get_response_bytes_count(self):
        payload = self.get_payload()
        offset = int(payload[1:4])
        size = int(payload[5:8])
        size = min(size, 2^31 - 1 - offset)
        return size * self.downlink_frame_bytes_count

    def get_requires_wait(self):
        return True

    def get_requires_send_receive(self):
        return False

# --------------------------
class SetPeriodicMessageTelecommandData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetPeriodicMessageTelecommandData, self).__init__(telecommand, 2)

class SendPeriodicMessageTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SendPeriodicMessageTelecommandData, self).__init__(telecommand, 2)

class TakePhotoTelecommandData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(TakePhotoTelecommandData, self).__init__(telecommand, 2)

    def is_scheduled(self):
        return True

class PurgePhotoTelecommandData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PurgePhotoTelecommandData, self).__init__(telecommand, 2)

class PowerCycleTelecommandData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PowerCycleTelecommandData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        state.reset_satellite()

class EraseBootTableEntryData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(EraseBootTableEntryData, self).__init__(telecommand, 2)

class WriteProgramPartData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(WriteProgramPartData, self).__init__(telecommand, 2)

class FinalizeProgramEntryData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(FinalizeProgramEntryData, self).__init__(telecommand, 2)

class OpenSailTelecommandData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(OpenSailTelecommandData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning('Did you mean: PerformSailExperiment?')

class StopSailDeploymentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(StopSailDeploymentData, self).__init__(telecommand, 2)

class GetPersistentStateData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(GetPersistentStateData, self).__init__(telecommand, 2)

class GetSunSDataSetsData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(GetSunSDataSetsData, self).__init__(telecommand, 2)

class SetTimeCorrectionConfigData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetTimeCorrectionConfigData, self).__init__(telecommand, 2)

class SetTimeData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetTimeData, self).__init__(telecommand, 2)

class TelecommandDataFactory(object):
    telecommands_map = dict({
        tc.SetBuiltinDetumblingBlockMaskTelecommand: SetBuiltinDetumblingBlockMaskTelecommandData,
        tc.SetAdcsModeTelecommand: SetAdcsModeTelecommandData,
        tc.SetAntennaDeployment: SetAntennaDeploymentData,
        tc.SetBootSlots: SetBootSlotsData,
        tc.EnterIdleState: EnterIdleStateData,
        tc.SendBeacon: SendBeaconData,
        tc.ResetTransmitterTelecommand: ResetTransmitterTelecommandData,
        tc.SetBitrate: SetBitrateData,
        tc.GetCompileInfoTelecommand: GetCompileInfoTelecommandData,
        tc.DisableOverheatSubmode: DisableOverheatSubmodeData,
        tc.PerformDetumblingExperiment: PerformDetumblingExperimentData,
        tc.AbortExperiment: AbortExperimentData,
        tc.PerformSunSExperiment: PerformSunSExperimentData,
        tc.PerformRadFETExperiment: PerformRadFETExperimentData,
        tc.PerformSailExperiment: PerformSailExperimentData,
        tc.PerformPayloadCommissioningExperiment: PerformPayloadCommissioningExperimentData,
        tc.PerformSADSExperiment: PerformSADSExperimentData,
        tc.PerformCameraCommissioningExperiment: PerformCameraCommissioningExperimentData,
        tc.CopyBootSlots: CopyBootSlotsData,
        tc.SetErrorCounterConfig: SetErrorCounterConfigData,
        tc.GetErrorCounterConfig: GetErrorCounterConfigData,
        tc.DownloadFile: DownloadFileData,
        tc.RemoveFile: RemoveFileData,
        tc.ListFiles: ListFilesData,
        tc.EraseFlash: EraseFlashData,
        tc.RawI2C: RawI2CData,
        tc.ReadMemory: ReadMemoryData,
        tc.SetPeriodicMessageTelecommand: SetPeriodicMessageTelecommandData,
        tc.SendPeriodicMessageTelecommand: SendPeriodicMessageTelecommandData,
        tc.TakePhotoTelecommand: TakePhotoTelecommandData,
        tc.PurgePhotoTelecommand: PurgePhotoTelecommandData,
        tc.PowerCycleTelecommand: PowerCycleTelecommandData,
        tc.EraseBootTableEntry: EraseBootTableEntryData,
        tc.WriteProgramPart: WriteProgramPartData,
        tc.FinalizeProgramEntry: FinalizeProgramEntryData,
        tc.OpenSailTelecommand: OpenSailTelecommandData,
        tc.StopSailDeployment: StopSailDeploymentData,
        tc.GetPersistentState: GetPersistentStateData,
        tc.GetSunSDataSets: GetSunSDataSetsData,
        tc.SetTimeCorrectionConfig: SetTimeCorrectionConfigData,
        tc.SetTime: SetTimeData
    })

    def get_telecommand_data(self, telecommand):
        telecommand_data_type = self.telecommands_map[type(telecommand)]
        return telecommand_data_type(telecommand)
