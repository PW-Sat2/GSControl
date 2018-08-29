## PW-Sat2 GSControl

This repository contains tools dedicated for PW-Sat2 Ground Station Operation Team as well as advanced radio amateurs (gnuradio part).

If you are interested in receiving of PW-Sat2 downlink signal find out more at: http://radio.pw-sat.pl/ and https://github.com/PW-Sat2/HAMRadio/wiki

Content of the repository:
 - gnuradio: GRC flow graphs for uplink (shared key needed) & downlink (signal sources from SDRs, downlink demodulator/frame decoder)
 - radio: console (iPython-based) to send telecommands and receive frames (the console connects to GRC part via ZMQ)
 - tools:
    - grafana_beacon_uploader: beacon uploader to OPER's internal database for Grafana tool
    - telemetry_files_analyzer: predict which telemetry file should be requested by the OPER team (`telemetry.current` / `telemetry.previous`)
    - decode_downlink_frames.py: downlink frames decoder
    - parse_beacon.py: methods to parse beacon frames
    - remote_files.py: tools for remote files (i.e. satellite files) handling, decoding photos, etc.
    - upload_software.py: script to upload software via radio

