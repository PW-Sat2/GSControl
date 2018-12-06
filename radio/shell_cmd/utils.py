import csv
import base64
import response_frames as rf
from StringIO import StringIO

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

    def merge_file_frames(frames1, frames2):
        all_chunks = [x for x in (frames1 + frames2) if isinstance(x, rf.common.FileSendSuccessFrame)]
        unique_ids = set([(x.seq(),x.correlation_id) for x in all_chunks])
        return map(lambda seq_cid: next((x for x in all_chunks if x.seq() == seq_cid[0] and x.correlation_id == seq_cid[1]), None), list(unique_ids))

    def merge_frames_by_payload(*frames):
        all_frames = [frame for subframes in frames for frame in subframes]
        seen = set()
        return [frame for frame in all_frames if tuple(frame.payload()) not in seen and not seen.add(tuple(frame.payload()))]

    def download_frames_from_sml(date_from, date_to):
        import urllib2
        from zipfile import ZipFile

        response = urllib2.urlopen('https://radio.pw-sat.pl/communication/log/export?f.from={}&f.to={}'.format(date_from, date_to))
        zip_file = ZipFile(StringIO(response.read()))

        parsed_frames = []

        for zip_info in zip_file.filelist:
            zip_content = zip_file.open(zip_info.filename)
            binary_frame = zip_content.read()
            decoded_frame = frame_decoder.decode(rcv.decode_kiss(binary_frame))
            parsed_frames.append(decoded_frame)

        return parsed_frames

    return {
        'send_and_parse_beacon': send_and_parse_beacon,
        'load_downlink_frames_file': load_downlink_frames_file,
        'merge_file_frames': merge_file_frames,
        'merge_frames_by_payload': merge_frames_by_payload,
        'download_frames_from_sml': download_frames_from_sml
    }