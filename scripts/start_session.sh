#!/bin/bash

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

source ${PWSAT_GS_GNURADIO}/setup_env.sh

if [ -z "$1" ]; then
    echo "Please specify session number"
    echo "Usage:"
    echo "./start_session.sh <session_number>"
    exit 1
fi
SESSION=$1

if [[ -f ${SESSION_FILE} ]]; then
    SESSION_NOW=$(<"${SESSION_FILE}")
    confirm "Session ${SESSION_NOW} already running. " || exit 1
fi

echo "Starting session ${SESSION}!"

source "$SELF_DIR/versions.sh"

echo -e "\n"

# update mission repository
git -C ${REPOS}/mission pull

# save versions file
${SELF_DIR}/versions.sh > /gs/${GS_NAME}_versions 2>&1

while [[ "${MISSION_MASTER_REV}" != "${MISSION_REV}" ]]; do
    if ! confirm_ask "Repo Mission NOT clean. Try again?"; then
        break
    fi

    # update mission repository
    git -C ${REPOS}/mission pull

    # save versions file
    ${SELF_DIR}/versions.sh > /gs/${GS_NAME}_versions 2>&1
done

if [[ "${MISSION_MASTER_REV}" != "${MISSION_REV}" ]]; then
    confirm "Repo Mission NOT clean."  || exit 1
fi

if [[ "${GSCONTROL_MASTER_REV}" != "${GSCONTROL_REV}" ]]; then
echo "UNCLEAN"
    #confirm "Repo GSControl NOT clean."  || exit 1
fi

# check if ham app is running
while [[ ! $(pgrep -fx ".*PW-Sat2_Ground_Station") ]]; do
    if ! confirm_ask "HAM app not running. Try again?"; then
        exit 1
    fi
done

ARCHIVE_FOLDER=/archive/${SESSION}
if [[ -d ${ARCHIVE_FOLDER} ]]; then
	confirm "Archive folder '${ARCHIVE_FOLDER}' already exists. " || exit 1
fi

DOWNLINK_FILE_IN_REPO=${REPOS_FOLDER}/mission/sessions/${SESSION}/artifacts/${GS_NAME}_downlink.frames
if [[ -f ${DOWNLINK_FILE_IN_REPO} ]]; then
	confirm "Downlink file '${DOWNLINK_FILE_IN_REPO}' already exists in repo mission! " || exit 1
fi

TASKLIST=${REPOS}/mission/sessions/${SESSION}/tasklist.py
# check if tasklist exist
while [[ ! -f ${TASKLIST} ]]; do
    if ! confirm_ask "Tasklist '${TASKLIST}' does not exists! Pull again?"; then
        break
    fi

    # update mission repository
    git -C ${REPOS}/mission pull

    # save versions file
    ${SELF_DIR}/versions.sh > /gs/${GS_NAME}_versions 2>&1
done

if [[ ! -f ${TASKLIST} ]]; then
	confirm "Tasklist '${TASKLIST}' does not exists! " || exit 1
fi

echo -e "\n"

# compile gnuradio
GRC="${GSCONTROL}/gnuradio"

compile_grc() {
    echo "Compiling ${1}..."
    TMP_FOLDER="$(dirname ${1})"
    if ! grcc $1 -d $TMP_FOLDER > /dev/null 2>&1; then
        echo "FAILED!"
    fi
}

echo -e "\n"

compile_grc ${GRC}/downlink/downlink-hier.grc
compile_grc ${GRC}/downlink/downlink-double.grc
compile_grc ${GRC}/downlink/source/funcube_source.grc
compile_grc ${GRC}/uplink/uplink.grc
compile_grc ${GRC}/uplink/uplink_watchdog.grc

# run gnuradio

run_grc() {
    cd /gs && python2.7 $1 &
}

run_grc ${GRC}/downlink/downlink_double.py
run_grc ${GRC}/uplink/uplink.py
run_grc ${GRC}/uplink/uplink_watchdog.py

echo "${SESSION}" > /gs/current_session.lock

# wait for user interaction at the beggining of the session
sleep 5
echo -e "\n\n"
read -r -p "Press ENTER to start funcube source"

run_grc ${GRC}/downlink/source/funcube_source.py
