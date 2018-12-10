import logging

save_frames_list()

save_file_lists()
save_beacons()

list_requested_files()

extract_downloaded_files()

save_persistent_state()

if session.has_artifact('telemetry.current'):
    if scope.upload:
        load_telemetry_file('telemetry.current')
    else:
        logging.warning('Not uploading telemetry.current. Pass -u flag to run upload')

if session.has_artifact('telemetry.previous'):
    if scope.upload:
        load_telemetry_file('telemetry.previous')
    else:
        logging.warning('Not uploading telemetry.current. Pass -u flag to run upload')