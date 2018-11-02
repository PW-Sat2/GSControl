class Limits(object):
    DOWNLINK_MAX_FRAME_SIZE = 235
    UPLINK_MAX_FRAME_SIZE = 200
    MAX_RESPONSE_FRAMES = 39

    def __init__(self):
        self.downlink_frame_size_limit = Limits.DOWNLINK_MAX_FRAME_SIZE
        self.uplink_frame_size_limit = Limits.UPLINK_MAX_FRAME_SIZE
        self.response_frames_limit = Limits.MAX_RESPONSE_FRAMES

    def max_downlink_frame_size(self):
        return self.downlink_frame_size_limit
    
    def max_uplink_frame_size(self):
        return self.uplink_frame_size_limit
    
    def max_response_frames(self):
        return self.response_frames_limit
        
