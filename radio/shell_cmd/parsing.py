from tools.remote_files import *
from pprint import pprint, pformat

def build(*args):
    def filter_file_chunks(frames, correlation_ids):
        import response_frames as rf

        result = frames
        result = filter(lambda f: isinstance(f, rf.common.FileSendSuccessFrame), result)
        result = filter(lambda f: f.correlation_id in correlation_ids, result)

        return result

    def parse_and_save_file_chunks(path, frames, correlation_ids):
        part_response = filter_file_chunks(frames, correlation_ids)
        part_response = map(lambda i: i.response, part_response)
        
        RemoteFileTools.save_chunks(path, part_response)

    def parse_and_save_photo_chunks(path, frames, correlation_ids):
        part_response = filter_file_chunks(frames, correlation_ids)
        part_response = map(lambda i: i.response, part_response)

        RemoteFileTools.save_photo(path, part_response)

    def parse_and_save_raw_and_photo(path, frames, correlation_ids):
        parse_and_save_photo_chunks(path + '.jpg', frames, correlation_ids)
        parse_and_save_file_chunks(path + '.raw', frames, correlation_ids)

    def parse_and_save_beacons(path, frames):
        from tools.parse_beacon import ParseBeacon
        import json

        beacons = map(ParseBeacon.parse, frames)
        beacons = filter(lambda x: x is not None, beacons)

        with open(path, 'w') as f:
            json.dump(beacons, f, default=ParseBeacon.convert_values, sort_keys=True, indent=4)

    def parse_and_save_file_list(path, frames, correlation_id):
        import response_frames as rf

        frames = filter(lambda f: isinstance(f, rf.file_system.FileListSuccessFrame), frames)
        frames = filter(lambda f: f.correlation_id == correlation_id, frames)

        files = []

        for frame in frames:
            part = RemoteFileTools.parse_file_list(frame)
            files.extend(part)


        text = pformat(files)
        print text

        with open(path, 'w') as f:
            f.write(text)

    return {
        'parse_and_save_file_chunks': parse_and_save_file_chunks,                     
        'parse_and_save_photo_chunks': parse_and_save_photo_chunks,
        'parse_and_save_raw_and_photo': parse_and_save_raw_and_photo,
        'parse_and_save_beacons': parse_and_save_beacons,
        'parse_and_save_file_list': parse_and_save_file_list
    }