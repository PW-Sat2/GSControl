#!/bin/bash

if [[ -z "$1" ]]; then
    echo "Please specify session number"
    echo "Usage:"
    echo "./download_all_frames.sh <session_number>"
    exit 1
fi

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

SESSION=$1

mkdir -p ${MISSION}/sessions/${SESSION}/artifacts/

cd ${GSCONTROL}/tools/radio_pwsat_pl/

python2 download_frame_files.py

mv -i all.frames ${MISSION}/sessions/${SESSION}/artifacts/
mv Turbo-Ola.bin ${MISSION}/
rm elka_downlink.frames
rm gliwice_downlink.frames


git -C ${MISSION} pull

git -C ${MISSION} add ${MISSION}/sessions/${SESSION}/artifacts/all.frames
git -C ${MISSION} add ${MISSION}/Turbo-Ola.bin

git -C ${MISSION} commit -m "${SESSION} - all"
git -C ${MISSION} log --stat

if confirm "Pushing to mission repo (all frames)."; then
    git -C ${MISSION} push
fi

