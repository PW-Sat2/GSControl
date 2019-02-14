#!/bin/bash

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

if [[ -z "$1" ]]; then
    echo "Please specify session number"
    echo "Usage:"
    echo "./archive.sh <session_number>"
    exit 1
fi

SESSION=$1
echo "SESSION: ${SESSION}"
ARCHIVE_FOLDER=/archive/${SESSION}

if [[ -d ${ARCHIVE_FOLDER} ]]; then
    confirm "Archive folder ${ARCHIVE_FOLDER} exists!" || exit 1
fi

mkdir -v ${ARCHIVE_FOLDER}

mv /gs/iq_data_from_current_session_after_doppler_correction ${ARCHIVE_FOLDER}/
mv /gs/iq_data_from_current_session_raw ${ARCHIVE_FOLDER}/

mv /gs/uplink_audio.wav ${ARCHIVE_FOLDER}/
mv /gs/uplink_frames ${ARCHIVE_FOLDER}/${GS_NAME}_uplink.frames
mv /gs/downlink_frames ${ARCHIVE_FOLDER}/${GS_NAME}_downlink.frames
mv /gs/watchdog_saved_frames_* ${ARCHIVE_FOLDER}/
mv /gs/${GS_NAME}_versions ${ARCHIVE_FOLDER}/
mv /gs/waterfall.jpg ${ARCHIVE_FOLDER}/${GS_NAME}_waterfall.jpg
mv /gs/waterfall.png ${ARCHIVE_FOLDER}/${GS_NAME}_waterfall.png

# Save mission artifacts

ls -l ${ARCHIVE_FOLDER}

# Save mission artifacts

REPOS_FOLDER="$(dirname $(dirname ${SELF_DIR}))"
ARTIFACT_FOLDER=${REPOS_FOLDER}/mission/sessions/${SESSION}/artifacts

git -C ${MISSION} pull

mkdir -vp ${ARTIFACT_FOLDER}

cp -vp ${ARCHIVE_FOLDER}/${GS_NAME}_downlink.frames ${ARTIFACT_FOLDER}/
cp -vp ${ARCHIVE_FOLDER}/${GS_NAME}_uplink.frames ${ARTIFACT_FOLDER}/
cp -vp ${ARCHIVE_FOLDER}/${GS_NAME}_versions ${ARTIFACT_FOLDER}/

ls -l ${ARTIFACT_FOLDER}

git -C ${MISSION} add ${ARTIFACT_FOLDER}/${GS_NAME}_downlink.frames ${ARTIFACT_FOLDER}/${GS_NAME}_uplink.frames ${ARTIFACT_FOLDER}/${GS_NAME}_versions
git -C ${MISSION} commit -m "${SESSION} - ${GS_NAME}"

if confirm "Pushing to mission repo."; then
    git -C ${MISSION} push
fi

# Upload waterfall to titan
mkdir -v /gs/${SESSION}
cp ${ARCHIVE_FOLDER}/${GS_NAME}_waterfall.png /gs/${SESSION}/${GS_NAME}_waterfall.png

scp -r -P 22 -i ~/.ssh/titan_key /gs/${SESSION}  pwsatwaterfall@titan.gajoch.pl:/home/pwsat/public/comm/waterfall/
rm -r /gs/${SESSION}