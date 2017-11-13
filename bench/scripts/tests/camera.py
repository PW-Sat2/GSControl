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
