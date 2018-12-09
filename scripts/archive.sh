#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

if [ -z "$1" ]; then
    echo "Please specify session number"
    echo "Usage:"
    echo "./archive.sh <session_number> <session_date>"
    exit 1
fi

if [[ -z "${GS_NAME}" ]]; then
    echo "Please specify GS_NAME in .bashrc"
    exit 1
fi

SESSION=$1
echo "SESSION: ${SESSION}"
ARCHIVE_FOLDER=/archive/${SESSION}

mkdir -v ${ARCHIVE_FOLDER}

mv /gs/iq_data_from_current_session_after_doppler_correction.raw ${ARCHIVE_FOLDER}/
mv /gs/iq_data_from_current_session_raw.raw ${ARCHIVE_FOLDER}/

mv /gs/uplink_audio.wav ${ARCHIVE_FOLDER}/
mv /gs/uplink_frames ${ARCHIVE_FOLDER}/${GS_NAME}_uplink.frames
mv /gs/downlink_frames ${ARCHIVE_FOLDER}/${GS_NAME}_downlink.frames

# Save mission artifacts

ls -l ${ARCHIVE_FOLDER}

# Save mission artifacts

REPOS_FOLDER=${DIR}/../../
ARTIFACT_FOLDER=${REPOS_FOLDER}/mission/sessions/${SESSION}/artifacts

mkdir -v ${ARTIFACT_FOLDER}

cp -vp ${ARCHIVE_FOLDER}/${GS_NAME}_downlink.frames ${ARTIFACT_FOLDER}/
cp -vp ${ARCHIVE_FOLDER}/${GS_NAME}_uplink.frames ${ARTIFACT_FOLDER}/

cd ${ARTIFACT_FOLDER}
ls -l

git add ${GS_NAME}_downlink.frames ${GS_NAME}_uplink.frames
git commit "${SESSION} - ${GS_NAME}"
git log --stat
git push
