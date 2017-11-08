from bench_init import *
import time

@make_test
def test_camera_telecommand(filename_base):
    photos_params = [{'Camera' : tc.camera.CameraLocation.Wing, 'Resolution' : tc.camera.PhotoResolution.p128},
                    {'Camera' : tc.camera.CameraLocation.Wing, 'Resolution' : tc.camera.PhotoResolution.p240},
                    {'Camera' : tc.camera.CameraLocation.Wing, 'Resolution' : tc.camera.PhotoResolution.p480},
                    {'Camera' : tc.camera.CameraLocation.Nadir, 'Resolution' : tc.camera.PhotoResolution.p128},
                    {'Camera' : tc.camera.CameraLocation.Nadir, 'Resolution' : tc.camera.PhotoResolution.p240},
                    {'Camera' : tc.camera.CameraLocation.Nadir, 'Resolution' : tc.camera.PhotoResolution.p480}]

    # Request photos
    for photo_params in photos_params:
        filename = filename_base + '_' + photo_params['Camera'] + '_' + photo_params['Resolution']
        send(tc.camera.TakePhoto(photo_params['Camera'], photo_params['Resolution'], 1, tc.camera.timedelta(0), filename))
        print filename, " : ", scripts.photo.wait_for_photo(filename + "_0", 200)
