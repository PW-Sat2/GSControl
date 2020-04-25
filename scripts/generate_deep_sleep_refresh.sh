#!/bin/bash

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common_functions.sh"


re='^[0-9]+$'
if ! [[ $1 =~ $re ]] ; then
   echo "error: Not a number" >&2; exit 1
fi

SESSION=$1

git -C $MISSION checkout master
git -C $MISSION pull

sed -i 's/\"auto\"/\"planned\"/' $MISSION/sessions/$SESSION/data.json
sed -i 's/\"sleep-beacon\"/\"refresh-deep-sleep\"/' $MISSION/sessions/$SESSION/data.json
sed -i 's/\"short_description\": \"\"/\"short_description\": \"Refresh Deep Sleep\"/' $MISSION/sessions/$SESSION/data.json

git -C $MISSION add $MISSION/sessions/$SESSION/data.json
git -C $MISSION commit -m "Session $SESSION - deep sleep refresh"

git -C $MISSION push
