#!/bin/bash

re='^[0-9]+$'
if ! [[ $1 =~ $re ]] ; then
   echo "error: Not a number" >&2; exit 1
fi

PWPATH=~/pwsat
SESSION=$1

git -C $PWPATH/mission checkout master
git -C $PWPATH/mission pull

sed -i 's/\"auto\"/\"planned\"/' $PWPATH/mission/sessions/$SESSION/data.json
sed -i 's/\"sleep-beacon\"/\"refresh-deep-sleep\"/' $PWPATH/mission/sessions/$SESSION/data.json
sed -i 's/\"short_description\": \"\"/\"short_description\": \"Refresh Deep Sleep\"/' $PWPATH/mission/sessions/$SESSION/data.json

git -C $PWPATH/mission add $PWPATH/mission/sessions/$SESSION/tasklist.py $PWPATH/mission/sessions/$SESSION/data.json
git -C $PWPATH/mission commit -m "Session $SESSION - deep sleep refresh"

git -C $PWPATH/mission push
