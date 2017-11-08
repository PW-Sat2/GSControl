from bench_init import *
import time

@make_test
def test_camera_telecommand(filename):
    # Request photo
    send(tc.camera.TakePhoto(tc.camera.CameraLocation.Wing, tc.camera.PhotoResolution.p128, 1, tc.camera.timedelta(0), filename))
    print(scripts.photo.wait_for_photo(filename + "_0", 200))
