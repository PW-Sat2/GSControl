
class State(object):
    DEFAULT_UPLINK_BIT_RATE = 1200
    DEFAULT_DOWNLINK_BIT_RATE = 1200
    ERASE_FLASH_EXPERIMENT_CORRELATION_ID = 0xBC
    RESERVED_CORRELATION_IDS = [ERASE_FLASH_EXPERIMENT_CORRELATION_ID]

    def __init__(self):
        self.corelation_ids = []
        self.downlink_bitrate = State.DEFAULT_DOWNLINK_BIT_RATE
        self.uplink_bitrate = State.DEFAULT_UPLINK_BIT_RATE

    def add_corelation_id(self, id, notes):
        if id is None:
            return

        if id in self.RESERVED_CORRELATION_IDS:
            notes.error('This correlation id is reserved: {}'.format(id))
        else:
            status = id in self.corelation_ids
            self.corelation_ids.append(id)
            if status:
                notes.error('Duplicated corelation id: {0}'.format(id))

    def change_downlink_bit_rate(self, new_bitrate):
        self.downlink_bitrate = new_bitrate

    def validate(self, notes):
        if self.downlink_bitrate != State.DEFAULT_DOWNLINK_BIT_RATE:
            notes.warning('Bitrate not restored ({})'.format(State.DEFAULT_DOWNLINK_BIT_RATE))

    def reset_transmitter(self):
        self.change_downlink_bit_rate(State.DEFAULT_DOWNLINK_BIT_RATE)
        
    def current_downlink_bitrate(self):
        return self.downlink_bitrate
    
    def current_uplink_bitrate(self):
        return self.uplink_bitrate

    def reset_satellite(self):
        self.reset_transmitter()
