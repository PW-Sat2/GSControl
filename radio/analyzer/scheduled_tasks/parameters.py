class Parameters:
    '''
    Extracts telecommand parameters from frame payload.
    '''
    END_OF_PATH_BYTE = 0x0

    @classmethod
    def get_parameters(self, frame_payload):
        params = []
        for index in range(0, self.END_OF_PARAMS_OFFSET):
            params.append(ord(frame_payload[index]))

        path = ""
        for index in range(self.END_OF_PARAMS_OFFSET, len(frame_payload)):
            if ord(frame_payload[index]) == self.END_OF_PATH_BYTE:
                break
            path = path + frame_payload[index]

        params.append(path)
        return params
