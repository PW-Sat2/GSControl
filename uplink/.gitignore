#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: AFSK 1200/2200 AX.25 uplink transmitter
# Author: Grzegorz Gajoch
# Generated: Fri Sep  8 23:32:02 2017
##################################################

from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
from optparse import OptionParser
import gr_kiss


class afsk_uplink(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "AFSK 1200/2200 AX.25 uplink transmitter")

        ##################################################
        # Variables
        ##################################################
        self.symb_rate = symb_rate = 1200
        self.samp_rate = samp_rate = 48000

        ##################################################
        # Blocks
        ##################################################
        self.kiss_nrzi_encode_0 = gr_kiss.nrzi_encode()
        self.kiss_kiss_to_pdu_0 = gr_kiss.kiss_to_pdu(True)
        self.kiss_hdlc_framer_0 = gr_kiss.hdlc_framer(preamble_bytes=50, postamble_bytes=7)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bf(([1200, 2200]), 1)
        self.blocks_vco_f_0 = blocks.vco_f(samp_rate, 6.238, 1)
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_char*1, samp_rate/symb_rate)
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.blks2_tcp_source_0 = grc_blks2.tcp_source(
        	itemsize=gr.sizeof_char*1,
        	addr='127.0.0.1',
        	port=1235,
        	server=True,
        )
        self.audio_sink_0 = audio.sink(samp_rate, '', True)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.kiss_hdlc_framer_0, 'out'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.kiss_kiss_to_pdu_0, 'out'), (self.kiss_hdlc_framer_0, 'in'))
        self.connect((self.blks2_tcp_source_0, 0), (self.kiss_kiss_to_pdu_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.kiss_nrzi_encode_0, 0))
        self.connect((self.blocks_vco_f_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_vco_f_0, 0), (self.audio_sink_0, 1))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.blocks_vco_f_0, 0))
        self.connect((self.kiss_nrzi_encode_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))

    def get_symb_rate(self):
        return self.symb_rate

    def set_symb_rate(self, symb_rate):
        self.symb_rate = symb_rate
        self.blocks_repeat_0.set_interpolation(self.samp_rate/self.symb_rate)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_repeat_0.set_interpolation(self.samp_rate/self.symb_rate)


def main(top_block_cls=afsk_uplink, options=None):

    tb = top_block_cls()
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
