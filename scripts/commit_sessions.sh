#!/bin/bash

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common_functions.sh"

git -C ${MISSION} pull

NEW_SESSIONS=${MISSION}/sessions

git -C ${MISSION} add ${NEW_SESSIONS}
git -C ${MISSION} commit -m "new sessions added"
git -C ${MISSION} push
