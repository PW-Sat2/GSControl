from bench_init import *
import time
from tools.tools import RandomString

@make_test
def test_camera_telecommand():
    # Request photo
    name = RandomString(4)
    send(tc.camera.TakePhoto(tc.camera.CameraLocation.Wing, tc.camera.PhotoResolution.p128, 1, tc.camera.timedelta(0), name))
    scripts.photo.wait_for_photo(name, 200)
