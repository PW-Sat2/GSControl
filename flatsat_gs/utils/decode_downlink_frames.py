import os
import sys

sys.path.append(os.path.join(os.path.dirname(
    __file__), '../build/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(
    __file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.parse_beacon import *
# from radio.radio_frame_decoder import *

import binascii

if __name__ == '__main__':
    filePath = sys.argv[1]
    with open(filePath, 'r') as f:
        lines = f.readlines()

    result = []

    for rawSingleResponse in lines:
        # print rawSingleResponse
        rawBase64Data = rawSingleResponse.split(',')[2]
        decodedFrame = ensure_byte_list(binascii.a2b_base64(rawBase64Data))

        decoder = response_frames.FrameDecoder(
            response_frames.frame_factories)

        decoded_frame = decoder.decode(decodedFrame[16:-2])

        result.append(decoded_frame)
        print type(decoded_frame)

    print len(result)
