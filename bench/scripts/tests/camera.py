from bench_init import *
import time

test_scenario_wing = [{'Camera' : tc.camera.CameraLocation.Wing, 'Resolution' : tc.camera.PhotoResolution.p128},
                    {'Camera' : tc.camera.CameraLocation.Wing, 'Resolution' : tc.camera.PhotoResolution.p240},
                    {'Camera' : tc.camera.CameraLocation.Wing, 'Resolution' : tc.camera.PhotoResolution.p480}]

test_scenario_nadir = [{'Camera' : tc.camera.CameraLocation.Nadir, 'Resolution' : tc.camera.PhotoResolution.p128},
                    {'Camera' : tc.camera.CameraLocation.Nadir, 'Resolution' : tc.camera.PhotoResolution.p240},
                    {'Camera' : tc.camera.CameraLocation.Nadir, 'Resolution' : tc.camera.PhotoResolution.p480}]

@make_test
def test_camera_telecommand(filename_base, test_scenario):
    # Request photos
    for photo_params in test_scenario:
        filename = filename_base + '_' + str(photo_params['Camera']) + '_' + str(photo_params['Resolution'])
        filename_obc = filename + "_0"
        PrintLog("Sending telecommand to take photo " + filename)
        send(tc.camera.TakePhoto(photo_params['Camera'], photo_params['Resolution'], 1, tc.camera.timedelta(0), filename))
        failed = None
        if scripts.photo.wait_for_file(filename_obc, 200) is True:
            scripts.fs.download_photo(filename_obc)
        else:
            PrintLog("Photo " + filename + " failed!")
            failed = filename

    assert(failed is None)
