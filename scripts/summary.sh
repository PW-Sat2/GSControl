#!/bin/bash

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common_functions.sh"

if [[ -z "$1" ]]; then
    echo "Please specify session number"
    echo "Usage:"
    echo "./summary.sh <session_number>"
    exit 1
fi

if [[ -z ${GRAFANA_URL} ]]; then
    echo "Grafana URL not defined!"
    read -r -p "Provide Grafana URL: " response
    echo "export GRAFANA_URL=${response}" >> ~/.bashrc
    source ~/.bashrc
fi

SESSION=$1
echo -e "SESSION: ${SESSION} Summary!\n"

git -C ${MISSION} pull

python2.7 ${GSCONTROL}/summary/run.py ${SESSION} -d ${GRAFANA_URL}

ARTIFACT_FOLDER=${MISSION}/sessions/${SESSION}/artifacts

git -C ${MISSION} add ${ARTIFACT_FOLDER}
git -C ${MISSION} commit -m "${SESSION} - summary"

if confirm "Pushing summary tool results to mission repo."; then
    git -C ${MISSION} push
fi

if confirm "Uploading summary to grafana."; then
    python2.7 ${GSCONTROL}/summary/run.py ${SESSION} -d ${GRAFANA_URL} -u
fi

if confirm "Ereasing zero beacons."; then
    python2.7 ${GSCONTROL}/tools/erase_zero_beacons.py ${GRAFANA_URL} --auto=True
fi
