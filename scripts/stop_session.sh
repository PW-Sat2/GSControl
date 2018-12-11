#!/bin/bash

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

if [[ ! -f ${SESSION_FILE} ]]; then
    echo "No active session running"
    exit 1
fi

SESSION=$(<"${SESSION_FILE}")

echo "Stopping session ${SESSION}!"

echo -e "\n"

pgrep -fx ".*/GSControl/gnuradio/uplink/uplink.py" | xargs kill
pgrep -fx ".*/GSControl/gnuradio/uplink/uplink_watchdog.py" | xargs kill
pgrep -fx ".*/GSControl/gnuradio/downlink/downlink_double.py" | xargs kill
pgrep -fx ".*/GSControl/gnuradio/downlink/source/funcube_source.py" | xargs kill

${SELF_DIR}/archive.sh ${SESSION}

echo -e "\n"

if confirm "Getting all.frames. Press 'y' when ready."; then
    ${SELF_DIR}/download_all_frames.sh ${SESSION}
fi

if confirm "Waiting for running Uber Session Summary Tool. Are you ready?"; then
    ${SELF_DIR}/summary.sh ${SESSION}
fi


rm ${SESSION_FILE}
