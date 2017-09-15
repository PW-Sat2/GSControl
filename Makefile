.PHONY: uplink run_uplink downlink run_downlink setup_env

uplink/uplink.py: uplink/uplink.grc
	grcc uplink/uplink.grc -d uplink

downlink/downlink.py:downlink/downlink.grc
	grcc downlink/downlink.grc -d downlink

uplink: uplink/uplink.py

downlink: downlink/downlink.py

all: uplink downlink

clean:
	rm -f uplink/uplink.py
	rm -f downlink/downlink.py


SETUP_ENV=~/prefix/default/setup_env.sh

run_downlink: downlink
	. $(SETUP_ENV) && python downlink/downlink.py

run_uplink: uplink
	. $(SETUP_ENV) && python uplink/uplink.py

