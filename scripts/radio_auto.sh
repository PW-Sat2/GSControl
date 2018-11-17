#!/bin/sh
echo "Radio Frequency Contoller started."
rigctld -m 214 -r /dev/radio -s 9600

