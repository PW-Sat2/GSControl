import csv
import base64

def build(sender, rcv, frame_decoder, *args):
    def send_and_parse_beacon():
        """
        Requests single beacon, waits for response, and parses it
        """
        from tools.parse_beacon import ParseBeacon
        from telecommand import SendBeacon

        sender.send(SendBeacon())
        data = rcv.decode_kiss(rcv.receive())
        beacon = frame_decoder.decode(data)

        return ParseBeacon.parse(beacon)

    def load_downlink_frames_file(file_name):
        """
        Loads frames CSV file and parse downlink frames.
        """
        parsed_frames = []

        with open(file_name, 'r') as csv_file:
            frames_reader = csv.reader(csv_file, delimiter=',')
            for row in frames_reader:
                if row[1] != 'D':
                    continue

                binary_frame = base64.b64decode(row[2])
                decoded_frame = frame_decoder.decode(rcv.decode_kiss(binary_frame))
                parsed_frames.append(decoded_frame)

        return parsed_frames


    return {
        'send_and_parse_beacon': send_and_parse_beacon,
        'load_downlink_frames_file': load_downlink_frames_file
    }