#!/bin/sh
echo "Radio Frequency Contoller started."
rigctl -m 214 -r /dev/radio -s 9600

