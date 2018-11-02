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


class TelecommandData(object):
    uplink_header_bytes_count = 3
    downlink_header_bytes_count = 3
    downlink_frame_bytes_count = 235

    def __init__(self, telecommand):
        self.telecommand = telecommand

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
        payload = self.get_payload()
        return payload[0]

    def get_response_bytes_count(self):
        raise NotImplementedError()

    def get_requires_wait(self):
        raise NotImplementedError()

    def get_requires_send_receive(self):
        raise NotImplementedError()

    def get_extra_notes(self):
        return []

    def get_frame_size(self):
        return len(self.telecommand.build())

    def check_frame_size(self, notes, limits):
        uplink_frame_size = self.get_frame_size()
        if uplink_frame_size > limits.max_uplink_frame_size():
            notes.error('Frame is too long: {0}'.format(uplink_frame_size))

    def process_common_command(self, state, notes, send_mode, wait_mode, limits):
        state.add_corelation_id(self.get_correlation_id(), notes)
        # state.count_uplink_frames(self.get_uplink_frame_count())
        # state.count_downlink_frames(self.get_downlink_frames_count())
        self.check_frame_size(notes, limits)       

        for extra_note in self.get_extra_notes():
            notes.info(extra_note)

        # if self.communication_mode != send_mode:
        #     notes.warning('Unexpected communication mode')

        # if self.wait_mode != wait_mode:
        #     notes.warning('Unexpected wait mode')

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

class SetBuiltinDetumblingBlockMaskTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SetBuiltinDetumblingBlockMaskTelecommandData, self).__init__(telecommand, 2)

class SetAdcsModeTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SetAdcsModeTelecommandData, self).__init__(telecommand, 2)

class SetAntennaDeploymentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SetAntennaDeploymentData, self).__init__(telecommand, 2)

class SetBootSlotsData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SetBootSlotsData, self).__init__(telecommand, 4)

class EnterIdleStateData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(EnterIdleStateData, self).__init__(telecommand, 2)

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
    def __init__(self, telecommand):
        super(DisableOverheatSubmodeData, self).__init__(telecommand, 2)

class PerformDetumblingExperimentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PerformDetumblingExperimentData, self).__init__(telecommand, 2)

class AbortExperimentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(AbortExperimentData, self).__init__(telecommand, 2)

class PerformSunSExperimentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PerformSunSExperimentData, self).__init__(telecommand, 2)

class PerformRadFETExperimentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PerformRadFETExperimentData, self).__init__(telecommand, 2)

class PerformSailExperimentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PerformSailExperimentData, self).__init__(telecommand, 2)

class PerformPayloadCommissioningExperimentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PerformPayloadCommissioningExperimentData, self).__init__(telecommand, 2)

class PerformSADSExperimentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PerformSADSExperimentData, self).__init__(telecommand, 2)

class PerformCameraCommissioningExperimentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PerformCameraCommissioningExperimentData, self).__init__(telecommand, 2)

class CopyBootSlotsData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(CopyBootSlotsData, self).__init__(telecommand, 2)

class SetErrorCounterConfigData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SetErrorCounterConfigData, self).__init__(telecommand, 2)

class GetErrorCounterConfigData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(GetErrorCounterConfigData, self).__init__(telecommand, 4)

    def get_correlation_id(self):
        return None

class DownloadFileData(TelecommandData):
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

class RemoveFileData(TelecommandData):
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
    def __init__(self, telecommand):
        super(ListFilesData, self).__init__(telecommand)

    def get_response_bytes_count(self):
        return 5 * self.downlink_frame_bytes_count # big unknown

    def get_requires_wait(self):
        return False

    def get_requires_send_receive(self):
        return False

class EraseFlashData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(EraseFlashData, self).__init__(telecommand, 3)

class RawI2CData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(RawI2CData, self).__init__(telecommand, self.downlink_frame_bytes_count)

class ReadMemoryData(TelecommandData):
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
    def __init__(self, telecommand):
        super(SetPeriodicMessageTelecommandData, self).__init__(telecommand, 2)

class SendPeriodicMessageTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SendPeriodicMessageTelecommandData, self).__init__(telecommand, 2)

class TakePhotoTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(TakePhotoTelecommandData, self).__init__(telecommand, 2)

class PurgePhotoTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PurgePhotoTelecommandData, self).__init__(telecommand, 2)

class PowerCycleTelecommandData(SimpleTelecommandData):
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
    def __init__(self, telecommand):
        super(OpenSailTelecommandData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning('Did you mean: PerformSailExperiment?')

class StopSailDeploymentData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(StopSailDeploymentData, self).__init__(telecommand, 2)

class GetPersistentStateData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(GetPersistentStateData, self).__init__(telecommand, 2)

class GetSunSDataSetsData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(GetSunSDataSetsData, self).__init__(telecommand, 2)

class SetTimeCorrectionConfigData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SetTimeCorrectionConfigData, self).__init__(telecommand, 2)

class SetTimeData(SimpleTelecommandData):
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
