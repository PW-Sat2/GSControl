#!/bin/bash

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

source ${PWSAT_GS_GNURADIO}/setup_env.sh

if [ -z "$1" ]; then
    echo "Please specify session number"
    echo "Usage:"
    echo "./start_auto_session.sh <session_number>"
    exit 1
fi
SESSION=$1

if [[ -f ${SESSION_FILE} ]]; then
    SESSION_NOW=$(<"${SESSION_FILE}")
    echo "Session ${SESSION_NOW} already running. "
    exit 2
fi

echo "Starting session ${SESSION}!"
source "$SELF_DIR/versions.sh"
echo -e "\n"

# save versions file
${SELF_DIR}/versions.sh > /gs/${GS_NAME}_versions 2>&1

# check if ham app is running
if [[ ! $(pgrep -fx ".*PW-Sat2_Ground_Station") ]]; then
    echo "HAM app not running"
    exit 3
fi

ARCHIVE_FOLDER=/archive/${SESSION}

if [[ -d ${ARCHIVE_FOLDER} ]]; then
	echo "Archive folder '${ARCHIVE_FOLDER}' already exists."
    exit 4
fi

# run gnuradio

run_grc() {
    cd /gs && python2.7 $1 &
}

GRC="${GSCONTROL}/gnuradio"

run_grc ${GRC}/downlink/downlink_double.py
run_grc ${GRC}/downlink/source/funcube_source.py
run_grc ${GRC}/uplink/uplink.py
run_grc ${GRC}/uplink/uplink_watchdog.py

echo "${SESSION}" > /gs/current_session.lock
