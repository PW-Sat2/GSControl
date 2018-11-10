import math
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from resources import *
from subsystems import *
from parameters import *


class TakePhotoParameters(Parameters):
    CORRELATION_ID_OFFSET = 0
    CAMERA_LOCATION_OFFSET = 1
    PHOTO_RESOLUTION_OFFSET = 2
    COUNT_OFFSET = 3
    DELAY_OFFSET_L = 4
    DELAY_OFFSET_H = 5
    END_OF_PARAMS_OFFSET = 6

    CAMERA_LOCATION_NADIR = 0x00
    CAMERA_LOCATION_WING = 0x01

    PHOTO_RESOLUTION_P128 = 0x03
    PHOTO_RESOLUTION_P240 = 0x05
    PHOTO_RESOLUTION_P480 = 0x07

    def __init__(self, frame_payload):
        self.correlation_id = self.get_parameters(frame_payload)[self.CORRELATION_ID_OFFSET]
        self.camera_location = self.get_parameters(frame_payload)[self.CAMERA_LOCATION_OFFSET]
        self.photo_resolution = self.get_parameters(frame_payload)[self.PHOTO_RESOLUTION_OFFSET]
        self.count = self.get_parameters(frame_payload)[self.COUNT_OFFSET]
        delay_l = self.get_parameters(frame_payload)[self.DELAY_OFFSET_L]
        delay_h = self.get_parameters(frame_payload)[self.DELAY_OFFSET_H]
        self.delay = (delay_h * 256) + delay_l


class TakePhoto:
    '''
    TakePhotoTelecommand adds a task to a photo queue: queue->delay->photos(count)
    Next TakePhotoTelecommand adds a new task to the photo queue.
    '''
    def __init__(self, frame_payload):
        self.parameters = TakePhotoParameters(frame_payload)

    def task_duration(self):
        photos_time = self.photos_time(self.parameters)
        return Duration(self.parameters.delay + photos_time)

    def downlink_frames_count(self):
        return self.photos_frames_count(self.parameters)

    def storage_usage(self):
        return Storage((self.photos_frames_count(self.parameters) * Comm.FULL_FRAME) / 1024.0)

    def energy_consumptions(self):
        energy_1200 = float(self.photos_energy_consumption(self.parameters) + self.downlink_energy_consumption(1200, self.parameters))
        energy_2400 = float(self.photos_energy_consumption(self.parameters) + self.downlink_energy_consumption(2400, self.parameters))
        energy_4800 = float(self.photos_energy_consumption(self.parameters) + self.downlink_energy_consumption(4800, self.parameters))
        energy_9600 = float(self.photos_energy_consumption(self.parameters) + self.downlink_energy_consumption(9600, self.parameters))
        return Energys([energy_1200, energy_2400, energy_4800, energy_9600])

    def downlink_durations(self):
        return Comm.downlink_durations(self.downlink_frames_count())

    @classmethod
    def photos_time(self, parameters):
        photo_time = Camera.PHOTO_128_TIME
        if parameters.photo_resolution == parameters.PHOTO_RESOLUTION_P240:
            photo_time = Camera.PHOTO_240_TIME
        if parameters.photo_resolution == parameters.PHOTO_RESOLUTION_P480:
            photo_time = Camera.PHOTO_480_TIME
        return photo_time * parameters.count

    @classmethod
    def photos_frames_count(self, parameters):
        photo_frames = Camera.PHOTO_128_MAX_FULL_FRAMES
        if parameters.photo_resolution == parameters.PHOTO_RESOLUTION_P240:
            photo_frames = Camera.PHOTO_240_MAX_FULL_FRAMES
        if parameters.photo_resolution == parameters.PHOTO_RESOLUTION_P480:
            photo_frames = Camera.PHOTO_480_MAX_FULL_FRAMES
        return parameters.count * photo_frames

    @classmethod
    def photos_energy_consumption(self, parameters):
        photo_3v3_energy_consumption = self.photos_time(parameters) * Camera.CAMERA_POWER / 3600.0  # Wh
        return Energy(((photo_3v3_energy_consumption * parameters.count) / Eps.EFFICIENCY_3V3) * 1000.0)

    @classmethod
    def downlink_energy_consumption(self, bitrate, parameters):
        transmission_time = Comm.downlink_frames_duration(self.photos_frames_count(parameters), bitrate)
        return Comm.downlink_energy_consumption(transmission_time)
