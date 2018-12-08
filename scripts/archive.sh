#!/bin/bash

if [ -z "$1" ]; then
    echo "Please specify session number"
    echo "Usage:"
    echo "./archive.sh <session_number> <session_date>"
    exit 1
fi
if [ -z "$2" ]; then
    echo "Please specify session date"
    echo "Usage:"
    echo "./archive.sh <session_number> <session_date>"
    exit 1
fi

echo $1 $2

mkdir -v /archive/$1_$2

cp -vp /gs/iq_data_from_current_session_after_doppler_correction.raw /archive/$1_$2/iq_data_from_current_session_after_doppler_correction.raw
cp -vp /gs/iq_data_from_current_session_raw.raw /archive/$1_$2/iq_data_from_current_session_raw.raw

cp -vp /gs/uplink_audio.wav /archive/$1_$2/uplink_audio.wav
cp -vp /gs/uplink_frames /archive/$1_$2/gliwice_uplink.frames

cp -vp /home/sat_user/downlink_frames /archive/$1_$2/gliwice_downlink.frames.bak
cp -vp /home/sat_user/downlink_all_frames /archive/$1_$2/gliwice_downlink_all.frames.bak
cp -vp /gs/downlink_frames /archive/$1_$2/gliwice_downlink.frames
cp -vp /gs/downlink_all_frames /archive/$1_$2/gliwice_downlink_all.frames

cp -vp /gs/iq_data_from_current_session_after_doppler_correction.raw /gs/iq_data_from_current_session_after_doppler_correction_$1_$2.raw
cp -vp /gs/iq_data_from_current_session_raw.raw /gs/iq_data_from_current_session_raw_$1_$2.raw
cp -vp /home/sat_user/downlink_frames /gs/gliwice_downlink_frames_$1_$2.frames.bak
cp -vp /home/sat_user/downlink_all_frames /gs/gliwice_downlink_all_frames_$1_$2.frames.bak
cp -vp /gs/downlink_frames /gs/gliwice_downlink_frames_$1_$2.frames
cp -vp /gs/downlink_all_frames /gs/gliwice_downlink_all_frames_$1_$2.frames

ls -l /archive/$1_$2

# Save mission artifacts

MISSION_FOLDER=/home/sat_user/gs/mission/sessions/$1

mkdir -v $MISSION_FOLDER/artifacts
cp -vp /gs/downlink_frames $MISSION_FOLDER/artifacts/gliwice_downlink.frames
cp -vp /gs/uplink_frames $MISSION_FOLDER/artifacts/gliwice_uplink.frames
ls -l $MISSION_FOLDER

