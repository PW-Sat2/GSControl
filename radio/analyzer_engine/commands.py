import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),
                '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__),
                '../..'))

import math
import telecommand as tc
from datetime import timedelta
from limits import Limits
from resources import *
from subsystems import *
from radio.task_actions import *
from devices.adcs import AdcsMode
from devices import CameraLocation, PhotoResolution

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
        return len(self.get_payload())

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
        return int((bytes_count + self.downlink_frame_bytes_count - 1) / self.downlink_frame_bytes_count)

    def get_correlation_id(self):
        return self.correlation_id

    def get_response_bytes_count(self):
        raise NotImplementedError()

    def get_requires_wait(self):
        return True

    def validate_wait_mode(self, wait_mode, notes):
        requires_wait = self.get_requires_wait()
        
        if requires_wait and wait_mode != WaitMode.Wait:
            notes.warning('Waiting is suggested')

        if not requires_wait and wait_mode != WaitMode.NoWait:
            notes.warning('Waiting is not recommended')

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

        if send_mode != SendReceive and send_mode != Send and send_mode != SendLoop:
            notes.error("Unsupported send mode")
        
        if send_mode == SendLoop:
            notes.info("In SendLoop mode - a telecommand in every <iteration_seconds>.")

        if self.get_requires_send_receive() and send_mode != SendReceive:
            notes.warning('SendReceive suggested')

        self.validate_wait_mode(wait_mode, notes)

        response_frame_count = self.get_downlink_frames_count()
        if self.get_downlink_frames_count() > limits.max_response_frames():
            notes.error('Too many response frames requested: {}. At most {} frames are allowed'.format(response_frame_count, limits.max_response_frames()))

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)

class NoTelecommand(object):
    def __init__(self, name, duration, info):
        self._name = name
        self._duration = duration
        self._info = info

    def telecommand_name(self, *args, **kwargs):
        return self._name

    def get_payload_size(self, *args, **kwargs):
        return 0

    def get_uplink_duration(self, bitrate):
        return self._duration

    def get_uplink_frames_count(self):
        return 0

    def get_downlink_duration(self, *args, **kwargs):
        return Duration(0)
    
    def get_downlink_energy_consumption(self, *args, **kwargs):
        return Energy(0)

    def get_downlink_frames_count(self, *args, **kwargs):
        return 0

    def is_scheduled(self):
        return False

    def process(self, state, notes, *args, **kwargs):
        if self._info:
            notes.info(self._info)

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

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        mask = self.telecommand._mask
        if mask != 0:
            notes.warning("Disabling detumbling is not recommended")


class SetAdcsModeTelecommandData(SimpleTelecommandData):
    ALLOWED_MODES = [-2, -1, 0, 1, 2]
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetAdcsModeTelecommandData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        mode = self.telecommand._mode
        if mode not in self.ALLOWED_MODES:
            notes.error("Invalid ADCS mode requested: {0}".format(mode))
        
        if mode == AdcsMode.ExperimentalDetumbling:
            notes.error("DO NOT ENABLE Experimental Detumbling. It is unstable.")
        elif mode == AdcsMode.ExperimentalSunpointing:
            notes.error("Do NOT ENABLE Experimental Sunpointing. It is not implemented.")
        elif mode == AdcsMode.BuiltinDetumbling:
            notes.warning("ADCS is power-on till next power cycle or till mode will be changed to stopped/disabled.")
            notes.info("First, set stopped mode before setting to built-in-detumbling mode.")
        elif mode == AdcsMode.Disabled:
            notes.warning("Disabling ADCS may be dangerous.")
    
    def is_scheduled(self):
        return True


class SetAntennaDeploymentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetAntennaDeploymentData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        disabled = int(self.telecommand._deployment_disabled)
        if not disabled:
            notes.warning("Why are you trying to enable antenna deployment?")

def extract_boot_slots(mask):
    list = []
    for i in range(0, 8, 1):
        if (mask & (1 << i)) != 0:
            list.append(i)
    return set(list)

class SetBootSlotsData(SimpleTelecommandData):
    UPPER_BOOT_SLOTS = 0x80
    SAFE_MOD_BOOT_SLOT = 0x40
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetBootSlotsData, self).__init__(telecommand, 4)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        primary = self.telecommand._primary
        failsafe = self.telecommand._failsafe
        if primary == failsafe:
            notes.error("Primary and failsafe boot slots should not be the same")
        if (primary & self.SAFE_MOD_BOOT_SLOT) == self.SAFE_MOD_BOOT_SLOT:
            notes.warning("Setting primary boot slots to safe mode is dangerous. It will also erase all data from flash memories")
        if (primary & self.UPPER_BOOT_SLOTS) == self.UPPER_BOOT_SLOTS or (failsafe & self.UPPER_BOOT_SLOTS) == self.UPPER_BOOT_SLOTS:
            notes.error("Upper boot slot should not be used for booting satellite")
        primary_slots = extract_boot_slots(primary)
        failsafe_slots = extract_boot_slots(failsafe)
        common = primary_slots.intersection(failsafe_slots)
        if (primary & failsafe) != 0:
            notes.error("there is at least one boot slot used as primary and failsafe boot slot")

        if len(primary_slots) != 3:
            notes.error("There should be 3 primary boot slots. There are {0} now".format(len(primary_slots)))

        if len(failsafe_slots) != 3:
            notes.error("There should be 3 failsafe boot slots. There are {0} now".format(len(failsafe_slots)))

class EnterIdleStateData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(EnterIdleStateData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.info('Prefer using Ping/SendBeacon telecommands instead')
        if self.telecommand._duration > 100:
            notes.warning('Prolonged COMM Idle state with significant power consumption (>= 100mWh)')

    def is_scheduled(self):
        return True

class SendBeaconData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SendBeaconData, self).__init__(telecommand, Limits().max_frame_payload_size())

class ResetTransmitterTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(ResetTransmitterTelecommandData, self).__init__(telecommand, 2)

    def get_requires_wait(self):
        return True

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
        index = int(self.telecommand._bitrate)
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
            notes.error('Invalid controller id: {0}'.format(self.telecommand._controller))

class PerformDetumblingExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformDetumblingExperimentData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.error('DO NOT START Detumbling experiment. It is unstable and will result in uncontrollable spinning')
        duration = self.telecommand._duration
        sampling_interval = self.telecommand.sampling_interval
    
        if duration.total_seconds() == 0:
            notes.error('Experiment duration is set to 0')
        elif duration > timedelta(hours = 12):
            notes.error('Experiment duration is too long: {}'.format(duration))

        if sampling_interval.total_seconds() == 0:
            notes.error('sampling interval is set to 0')        

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
    
    def is_scheduled(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        path = self.telecommand.file_name

        if len(path) + 1 > 30:
            notes.error("Path is too long: {0} characters. 30 characters including null terminator are allowed.".format(len(path) + 1))
        elif len(path) == 0:
            notes.error("Experiment file path is empty")

class PerformRadFETExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformRadFETExperimentData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        path = self.telecommand.output_file_name
        if len(path) + 1 > 30:
            notes.error("Path is too long: {0} characters. 30 characters including null terminator are allowed.".format(len(path) + 1))
        elif len(path) == 0:
            notes.error("Experiment file path is empty")

    def is_scheduled(self):
        return True

class PerformSailExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformSailExperimentData, self).__init__(telecommand, 2)
    
    def is_scheduled(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning('This command effectively ends satellite mission')

class PerformPayloadCommissioningExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformPayloadCommissioningExperimentData, self).__init__(telecommand, 2)

    def is_scheduled(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        path = self.telecommand.file_name
        if len(path) + 1 > 30:
            notes.error("Path is too long: {0} characters. 30 characters including null terminator are allowed.".format(len(path) + 1))
        elif len(path) == 0:
            notes.error("Experiment file path is empty")

class PerformSADSExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformSADSExperimentData, self).__init__(telecommand, 2)
    
    def is_scheduled(self):
        return True

class PerformCameraCommissioningExperimentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(PerformCameraCommissioningExperimentData, self).__init__(telecommand, 2)
    
    def is_scheduled(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        path = self.telecommand.file_name
        if len(path) + 1 > 30:
            notes.error("Path is too long: {0} characters. 30 characters including null terminator are allowed.".format(len(path) + 1))
        elif len(path) == 0:
            notes.error("Experiment file path is empty")

class CopyBootSlotsData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(CopyBootSlotsData, self).__init__(telecommand, 2)
    
    def is_scheduled(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        source = self.telecommand.source_mask
        target = self.telecommand.target_mask
        source_list = extract_boot_slots(source)
        target_list = extract_boot_slots(target)

        if (source & target) != 0:
            notes.error('Boot slot cannot be source and target at the same time')

        if len(target_list) == 0:
            notes.error('Target boot slots are not specified')

        if len(source_list) != 3:
            notes.error('Invalid number of source boot slots: {0}. There should be {1}'.format(len(source_list), 3))
        
        if len(target_list) > 3:
            notes.error('Too many target boot slots: {}'.format(len(target_list)))

        for e in source_list:
            if e > 5:
                notes.error('Invalid source boot slot number: {}'.format(e))

        for e in target_list:
            if e > 5:
                notes.error('Invalid target boot slot number: {}'.format(e))


class SetErrorCounterConfigData(SimpleTelecommandData):
    KNOWN_ERROR_COUNTERS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetErrorCounterConfigData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        configs = self.telecommand._configs
        if len(configs) == 0:
            notes.warning("Error counter configurations are missing")
        elif len(configs) > 14:
            notes.errors("Too many error counter configurations")

        devices = set([])
        for entry in configs:
            if entry.device not in self.KNOWN_ERROR_COUNTERS:
                notes.error("Invalid error counter identifier: {0}".format(entry.device))
            if entry.limit <= entry.increment:
                notes.warning("Error counter for device: {0} will hit limit with single error".format(entry.device))
            if entry.increment <= entry.decrement:
                notes.warning("Error counter for device {0} is set to be too forgiving for errors".format(entry.device))
            if entry.increment == 0:
                notes.warning("Error counter for device {0} is disabled".format(entry.device))
            if entry.decrement == 0:
                notes.warning("Device {0} is not allowed to recover from errors".format(entry.device))
            devices.add(entry.device)

        if len(devices) != len(configs):
            notes.error("There are multiple configurations for single device")

class GetErrorCounterConfigData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(GetErrorCounterConfigData, self).__init__(telecommand, 4)

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
        return seqs_count * Limits().max_frame_payload_size()

    def get_requires_wait(self):
        return True

    def get_requires_send_receive(self):
        return False

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        path = self.telecommand._path
        if len(path) == 0:
            notes.error('File path is empty')

        seqs = self.telecommand._seqs
        if len(seqs) > limits.max_response_frames():
            notes.error('Too many sequences are requested for download: {0}'.format(len(seqs)))
        elif len(seqs) == 0:
            notes.error('List of file blocks is empty')

        ids = set([])
        for e in seqs:
            ids.add(e)
            if e > 600 * 1024 / limits.max_correlated_frame_payload_size():
                notes.warning('This file block id is suspiciously big: {}'.format(e))
        
        if len(ids) != len(seqs):
            notes.error('There are duplicated block identifiers')

class RemoveFileData(TelecommandData):
    MAX_PATH_LENGTH = 192
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

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        path = self.telecommand._path
        if len(path) > self.MAX_PATH_LENGTH:
            notes.error('Path is too long: {0} characters. {1} characters are allowed'.format(len(path), self.MAX_PATH_LENGTH))
        elif len(path) == 0:
            notes.error("Experiment file path is empty")
        if path == 'telemetry.current' or path == '/telemetry.current' or path == './telemetry.current':
            notes.warning("Removing current telemetry file is not recommended")
        if path == 'telemetry.previous' or path == '/telemetry.previous' or path == './telemetry.previous':
            notes.warning("Removing previous telemetry file is not recommended")

class ListFilesData(TelecommandData):
    MAX_PATH_LENGTH = 194
    @set_correlation_id
    def __init__(self, telecommand):
        super(ListFilesData, self).__init__(telecommand)

    def get_response_bytes_count(self):
        return 5 * Limits().max_frame_payload_size()

    def get_requires_wait(self):
        return False

    def get_requires_send_receive(self):
        return False
        
    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        path = self.telecommand._path
        if (len(path) + 1) > self.MAX_PATH_LENGTH:
            notes.error('Path is too long: {0} characters. {1} characters including null terminator are allowed'.format(len(path) + 1, self.MAX_PATH_LENGTH))
        elif len(path) == 0:
            notes.error("Experiment file path is empty")

class EraseFlashData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(EraseFlashData, self).__init__(telecommand, 3)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning('Do you really intend to erase entire filesystem?')
    

class RawI2CData(SimpleTelecommandData):
    BUS_DEVICES = [
        0x10,    # Imtq
        0x31,    # Primary Antenna
        0x35,    # EPS A
        0x60,    # Comm Receiver
        0x61,    # Comm Transmitter,
    ]

    PAYLOAD_DEVICES = [
        0x30,    # Payload
        0x32,    # Backup Antenna
        0x36,    # EPS B
        0x44,    # Suns
        0x51,    # RTC
        0x68,    # Gyroscope
    ]

    @set_correlation_id
    def __init__(self, telecommand):
        super(RawI2CData, self).__init__(telecommand, Limits().max_frame_payload_size())

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning("This is last resort command do not use it recklessly")

        address = self.telecommand._address
        bus = self.telecommand._busSelect
        if bus != 0 and bus != 1:
            notes.error("Invalid i2c bus: {0}. 0 or 1 are allowed".format(bus))

        if bus == 0 and address not in RawI2CData.BUS_DEVICES:
            notes.error('There is no device at address {0} on primary i2c bus'.format(address))

        if bus == 1 and address not in RawI2CData.PAYLOAD_DEVICES:
            notes.error('There is no device at address {0} on payload i2c bus'.format(address))

        data = self.telecommand._data
        if len(data) == 0:
            notes.warning("Empty i2c frame detected")

class ReadMemoryData(TelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(ReadMemoryData, self).__init__(telecommand)

    def get_response_bytes_count(self):
        return self.telecommand.size

    def get_requires_wait(self):
        return True

    def get_requires_send_receive(self):
        return False

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        size = self.telecommand.size
        offset = self.telecommand.offset
        if size == 0:
            notes.error('Empty memory block requested')

        if (size + offset) > (pow(2, 32) - 1):
            notes.error('Wrapping around memory space is not allowed')

# --------------------------
class SetPeriodicMessageTelecommandData(SimpleTelecommandData):
    INTERVAL_LIMIT = {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 4,
        6: 5
    }
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetPeriodicMessageTelecommandData, self).__init__(telecommand, 2)
    
    def is_scheduled(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        interval = self.telecommand._interval_minutes
        count = self.telecommand._repeat_count
        if count in self.INTERVAL_LIMIT:
            if interval < self.INTERVAL_LIMIT[count]:
                notes.error('Power budget strain is too big')
        else:
            notes.error('Too many periodic messages are scheduled. Power budget strain is too big')
            

class SendPeriodicMessageTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(SendPeriodicMessageTelecommandData, self).__init__(telecommand, 200)

    def get_downlink_frames_count(self):
        return self.telecommand.count

class TakePhotoTelecommandData(SimpleTelecommandData):
    ALLOWED_LOCATIONS = [CameraLocation.Nadir, CameraLocation.Wing]
    ALLOWED_RESOLUTIONS = [PhotoResolution.p128, PhotoResolution.p240, PhotoResolution.p480]
    MAX_PICTURE_COUNT = 30
    MAX_PICTURE_PATH_LENGTH = 30
    @set_correlation_id
    def __init__(self, telecommand):
        super(TakePhotoTelecommandData, self).__init__(telecommand, 2)

    def is_scheduled(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        camera_location = self.telecommand._camera_id
        resolution = self.telecommand._resolution
        count = self.telecommand._picture_count
        path = self.telecommand._picture_path

        if not camera_location in self.ALLOWED_LOCATIONS:
            notes.error('Invalid camera location: {}'.format(camera_location))

        if not resolution in self.ALLOWED_RESOLUTIONS:
            notes.error('Invalid photo resolution: {}'.format(resolution))

        if count >= self.MAX_PICTURE_COUNT:
             notes.error('Too many pictures requested: {}'.format(count))

        if len(path) == 0:
            notes.error('Photo path is empty')
        elif len(path) > self.MAX_PICTURE_PATH_LENGTH:
            notes.error('Photo path is too long: {0} characters. {1} characters are allowed.'.format(len(path), self.MAX_PICTURE_PATH_LENGTH))


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
        notes.warning("Communication with satellite will be unavailable for the next few minutes")
        if wait_mode != WaitMode.Wait:
            notes.error("Wait is suggested as next telecommand will most likely will not be processed")

class EraseBootTableEntryData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(EraseBootTableEntryData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        length = len(self.telecommand._entries)
        if length == 0:
            notes.error('Boot slot list is empty')
        elif length > 5:
            notes.error("Are you trying to brick the satellite?")
        elif length > 3:
            notes.error("Too many boot entries will be erased: {0}. At most 3 should be erased".format(length))      

        groups = set([])
        for e in self.telecommand._entries:
            if e >= 6 or e < 0:
                notes.error("Invalid boot entry id: {0}.".format(e))
            groups.add(e / 3)

        if len(groups) > 1:
            notes.error("Erasing boot entries from more than one set is an error")      

class WriteProgramPartData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(WriteProgramPartData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        length = len(self.telecommand._entries)
        offset = self.telecommand._offset
        if length == 0:
            notes.error('Boot slot list is empty')
        elif length > 5:
            notes.error("Are you trying to brick the satellite?")
        elif length > 3:
            notes.error("Too many boot entries will be updated: {0}. At most 3 should be written".format(length))

        groups = set([])
        for e in self.telecommand._entries:
            if e >= 6 or e < 0:
                notes.error("Invalid boot entry id: {0}.".format(e))
            groups.add(e / 3)

        if len(groups) > 1:
            notes.error("Writing to boot entries from more than one set is an error")  

        if offset > 511 * 1024:
            notes.error('Invalid program offset: {}'.format(offset))

        elif offset > 230 * 1024:
            notes.warning('Are you sure this offset is correct: {}?'.format(offset))

class FinalizeProgramEntryData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(FinalizeProgramEntryData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        entries = self.telecommand._entries
        length = self.telecommand._length
        name = self.telecommand._name

        if len(entries) == 0 or len(entries) > 3:
            notes.error('Invalid number of finalized boot slots: {}'.format(len(entries)))

        if len(name) > 30:
            notes.error('Too long boot slot name: {}'.format(len(name))) 

        if length < 10 * 1024:
            notes.error('Invalid program length: {}'.format(length))
        elif length < 50 * 1024:
            notes.warning('Suspiciously short program length: {}'.format(length))

        for e in entries:
            if e > 5:
                notes.error('Invalid boot slot number: {}'.format(e))


class OpenSailTelecommandData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(OpenSailTelecommandData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning('Did you mean: PerformSailExperiment?')
        notes.warning('This command effectively ends satellite mission')

class StopSailDeploymentData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(StopSailDeploymentData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        notes.warning('This telecommand disables automatic sail deployment in OBC')

class GetPersistentStateData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(GetPersistentStateData, self).__init__(telecommand, 2)

class GetSunSDataSetsData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(GetSunSDataSetsData, self).__init__(telecommand, 89)

class SetTimeCorrectionConfigData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetTimeCorrectionConfigData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        mission_time_weight = self.telecommand._missionTimeWeight
        external_time_weight = self.telecommand._externalTimeWeight
        if mission_time_weight == 0 and external_time_weight == 0:
            notes.error('Both weights cannot be zero at the same time')
        if mission_time_weight == 0:
           notes.warning('Disabling mission time as time correction source')
        if external_time_weight == 0:
           notes.warning('Disabling external time as time correction source')

class SetTimeData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(SetTimeData, self).__init__(telecommand, 2)

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        newTime = self.telecommand._newTime
        
        if newTime < timedelta(minutes = 40):
            notes.error('New time is in mission silent period')
        elif newTime < timedelta(hours = 4):
            notes.warning('new time is in LEOP mission phase')
        elif newTime >= timedelta(days = 40):
            notes.error('New time is after mission active phase. Are you trying to end mission? Did you mean: OpenSail?')


class PingTelecommandData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(PingTelecommandData, self).__init__(telecommand, 4)

class LittleOryxEchoData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(LittleOryxEchoData, self).__init__(telecommand, 1)

class LittleOryxRebootData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(LittleOryxRebootData, self).__init__(telecommand, 1)

    
    def get_requires_wait(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        state.reset_satellite()
        notes.warning("Communication with satellite will be unavailable for the next few seconds")
        if wait_mode != WaitMode.Wait:
            notes.error("Wait is suggested as next telecommand will most likely will not be processed")

class LittleOryxRebootToNormalData(SimpleTelecommandData):
    def __init__(self, telecommand):
        super(LittleOryxRebootToNormalData, self).__init__(telecommand, 1)
        
    def get_requires_wait(self):
        return True

    def process(self, state, notes, send_mode, wait_mode, limits):
        self.process_common_command(state, notes, send_mode, wait_mode, limits)
        state.reset_satellite()
        notes.warning("Communication with satellite will be unavailable for the next few minutes")
        if wait_mode != WaitMode.Wait:
            notes.error("Wait is suggested as next telecommand will most likely will not be processed")

class LittleOryxDelayRebootToNormalData(SimpleTelecommandData):
    @set_correlation_id
    def __init__(self, telecommand):
        super(LittleOryxDelayRebootToNormalData, self).__init__(telecommand, 2)
          

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
        tc.SetTime: SetTimeData,
        tc.PingTelecommand: PingTelecommandData,
        tc.little_oryx.Echo: LittleOryxEchoData,
        tc.little_oryx.Reboot: LittleOryxRebootData,
        tc.little_oryx.RebootToNormal: LittleOryxRebootToNormalData,
        tc.little_oryx.DelayRebootToNormal: LittleOryxDelayRebootToNormalData,
    })

    def get_telecommand_data(self, telecommand):
        telecommand_data_type = self.telecommands_map[type(telecommand)]
        return telecommand_data_type(telecommand)

    def handle_print(self, message):
        if not isinstance(message, basestring):
            raise Exception('Print command requires string argument. Got: "{}"'.format(type(message)))
        return NoTelecommand('Print', Duration(0), 'Print: "{}"'.format(message))
    
    def handle_send_loop(self, loop_arguments):
        REQUIRED_NO_ARGUMENTS = 2

        try:
            telecommand = loop_arguments[0]

            if not len(loop_arguments) == REQUIRED_NO_ARGUMENTS:
                raise Exception('SendLoop command requires two arguments in a list [telecommand, iteration_seconds]. Got: {} arguments.'.format(len(loop_arguments)))
        
            iteration_seconds = loop_arguments[1]
        except TypeError:
            raise Exception('SendLoop command requires two arguments in a list [telecommand, iteration_seconds]. It is not a list.')
        
        if not isinstance(iteration_seconds, int):
            raise Exception('SendLoop command requires two arguments in a list [telecommand, iteration_seconds]. Got wrong iteration_seconds: "{}"'.format(type(iteration_seconds)))

        return self.get_telecommand_data(telecommand)

    def handle_sleep(self, time):
        if not isinstance(time, int):
            raise Exception('Sleep command requires integer argument. Got: "{}"'.format(type(time)))
        return NoTelecommand('Sleep', Duration(int(time)), 'Sleep for {} seconds'.format(int(time)))

    def get_analyzer(self, mode, argument):
        generator = TelecommandDataFactory.mode_map[mode]
        return generator(self, argument)

    mode_map = dict({
        Send: get_telecommand_data,
        SendReceive: get_telecommand_data,
        SendLoop: handle_send_loop,
        Print: handle_print,
        Sleep: handle_sleep
    })