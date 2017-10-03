from PyQt4 import Qt
from gnuradio import analog
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import sip
import sys
from gnuradio import qtgui

from distutils.version import StrictVersion

from PyQt4 import Qt
import sys

from uplink import uplink

import thread, time


class Uplink(object):
    def __init__(self):
        thread.start_new_thread(self.run_thread, ())
        time.sleep(5)

    def wait_stable(self):
        time.sleep(5)
        
    def set_attenuation(self, att):
        self.tb._attenuation_win.d_widget.counter.setValue(att)
        self.wait_stable()
                
    def set_carrier(self, freq):
        self.tb._carrier_win.d_widget.counter.setValue(freq)
        self.wait_stable()
    
    def set_audio(self, lower, higher):
        self.tb._audio_higher_win.d_widget.counter.setValue(higher)
        self.tb._audio_lower_win.d_widget.counter.setValue(lower)
        self.wait_stable()
        
    def run_thread(self):
        if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
            style = gr.prefs().get_string('qtgui', 'style', 'raster')
            Qt.QApplication.setGraphicsSystem(style)
        self.qapp = Qt.QApplication(sys.argv)
                
        self.tb = uplink()
        self.tb.start()
        self.tb.show()
                        
        def quitting():
            self.tb.stop()
            self.tb.wait()
                            
        self.qapp.connect(self.qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
        self.qapp.exec_()

if __name__ == "__main__":
    ul = Uplink()
    ul.set_carrier(146e6)
    print "Enter to exit"
    raw_input()
                            
