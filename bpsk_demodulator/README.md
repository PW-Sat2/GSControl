## BPSK demodulator

To run the BPSK demodulator in GNU Radio, please follow these steps:
* Load an IQ *.wav file, exported from SDRsharp (2.56MHz sampling rate)
* Select paths for both *.wav and *.txt files
* Launch the GNU Radio project
* Open the *.wav file in Audacity and check that these waveforms were properly generated
* The *.txt file contains demodulated output bit-stream (one char means one bit)

Tools needed:
* SDRsharp: http://airspy.com/download/
* GNU Radio: http://gnuradio.org
* Audacity: http://www.audacityteam.org

IQ files for all baudrates are available at PW-Sat2 FTP: ftp:/communication/pomiary/28_01_2017/nasluch_28_01_2017/