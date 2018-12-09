#!/bin/bash

if [[ -z "$1" ]]; then
    echo "Please specify session number"
    echo "Usage:"
    echo "./download_all_frames.sh <session_number>"
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
SESSION=$1

GS_REPOS=${DIR}/../../

cd ${DIR}/../tools/radio_pwsat_pl/

mkdir -p ${GS_REPOS}/mission/sessions/${SESSION}/artifacts/

python2 download_frame_files.py

mv -i all.frames ${GS_REPOS}/mission/sessions/${SESSION}/artifacts/
mv Turbo-Ola.bin ${GS_REPOS}/mission/
rm elka_downlink.frames
rm gliwice_downlink.frames

cd ${GS_REPOS}/mission/
git pull --rebase

git add sessions/${SESSION}/artifacts/all.frames
git add Turbo-Ola.bin

git commit -m "${SESSION} - all"
git push

