.PHONY: uplink run_uplink downlink run_downlink setup_env

uplink/uplink.py: uplink/uplink.grc
	. $(SETUP_ENV) && grcc $< -d uplink

downlink/downlink.py:downlink/downlink.grc
	. $(SETUP_ENV) && grcc $< -d downlink

downlink/source/funcube_source.py: downlink/source/funcube_source.grc
	. $(SETUP_ENV) && grcc $< -d downlink/source

uplink: uplink/uplink.py

downlink: downlink/downlink.py

funcube: downlink/source/funcube_source.py

all: uplink downlink

clean:
	rm -f uplink/uplink.py
	rm -f downlink/downlink.py
	rm -f downlink/source/funcube_source.py


SETUP_ENV=~/prefix/default/setup_env.sh

run_downlink: downlink funcube
	. $(SETUP_ENV) && python downlink/source/funcube_source.py &
	. $(SETUP_ENV) && python downlink/downlink.py &

run_uplink: uplink
	. $(SETUP_ENV) && python uplink/uplink.py


