import logging

save_frames_list()

save_file_lists()
save_beacons()

list_requested_files()

extract_downloaded_files()


if session.has_artifact('telemetry.current'):
    load_telemetry_file('telemetry.current')

if session.has_artifact('telemetry.previous'):
    load_telemetry_file('telemetry.previous')