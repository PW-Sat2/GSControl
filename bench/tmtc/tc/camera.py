import telecommand.photo as photo
from response_frames.common import PhotoSuccessFrame
from devices.camera import CameraLocation, PhotoResolution
from datetime import timedelta


class TakePhoto(object):
    def __init__(self, camera, resolution, count, delay, path):
        self.camera = camera
        self.resolution = resolution
        self.count = count
        self.delay = delay
        self.path = path

    def send(self, tmtc):
        return tmtc.send_tc_with_response(photo.TakePhotoTelecommand,
                                          PhotoSuccessFrame,
                                          self.camera,
                                          self.resolution,
                                          self.count,
                                          self.delay,
                                          self.path)
