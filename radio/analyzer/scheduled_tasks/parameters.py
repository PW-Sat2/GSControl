class Parameters:
    '''
    Extracts telecommand parameters from frame payload.
    '''
    CORRELATION_ID_OFFSET = 0
    END_OF_PATH_BYTE = 0x0
    PATH_INCLUDED = True

    @classmethod
    def get_parameters(self, frame_payload):
        params = []
        for index in range(0, self.END_OF_PARAMS_OFFSET):
            value = 0
            try:
                value = ord(frame_payload[index])
            except TypeError:
                value = frame_payload[index]
            params.append(value)

        if self.PATH_INCLUDED:
            path = ""
            for index in range(self.END_OF_PARAMS_OFFSET, len(frame_payload)):
                value = 0
                try:
                    value = ord(frame_payload[index])
                except TypeError:
                    value = frame_payload[index]
                if value == self.END_OF_PATH_BYTE:
                    break
                path = path + str(frame_payload[index])

            params.append(path)
        return params
