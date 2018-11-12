class Limits(object):
    DOWNLINK_MAX_FRAME_SIZE = 235
    MAX_RESPONSE_FRAMES = 38
    DOWNLINK_HEADER_SIZE = 3
    DOWNLINK_CORRELATED_FRAME_HEADER_SIZE = 1

    def __init__(self):
        self.downlink_frame_size_limit = Limits.DOWNLINK_MAX_FRAME_SIZE
        self.response_frames_limit = Limits.MAX_RESPONSE_FRAMES

    def max_downlink_frame_size(self):
        return self.downlink_frame_size_limit
        
    def max_response_frames(self):
        return self.response_frames_limit

    def max_correlated_frame_payload_size(self):
        return self.DOWNLINK_MAX_FRAME_SIZE - self.DOWNLINK_HEADER_SIZE - self.DOWNLINK_CORRELATED_FRAME_HEADER_SIZE
