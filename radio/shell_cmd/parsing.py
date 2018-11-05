from tools.remote_files import *
from pprint import pprint, pformat

def build(*args):
    def filter_file_chunks(frames, correlation_ids):
        import response_frames as rf

        result = frames
        result = filter(lambda f: isinstance(f, rf.common.FileSendSuccessFrame), result)
        result = filter(lambda f: f.correlation_id in correlation_ids, result)

        return result

    def extract_and_save_file_chunks(path, frames, correlation_ids):
        """
        Extracts file chunks from frames list

        path - path to file that will be reconstructed from parts
        frames - frames list
        correlation_ids - list of correlation ids that will be parsed

        Only FileSendSuccess frames with matching correlation id are saved
        """
        part_response = filter_file_chunks(frames, correlation_ids)
        part_response = map(lambda i: i.response, part_response)
        
        RemoteFileTools.save_chunks(path, part_response)

    def extract_and_save_photo_chunks(path, frames, correlation_ids):
        """
        Extracts photo chunks from frames list

        path - path to file that will be reconstructed from parts
        frames - frames list
        correlation_ids - list of correlation ids that will be parsed

        Only FileSendSuccess frames with matching correlation id are saved
        """
        part_response = filter_file_chunks(frames, correlation_ids)
        part_response = map(lambda i: i.response, part_response)

        RemoteFileTools.save_photo(path, part_response)

    def extract_and_save_raw_and_photo(path, frames, correlation_ids):
        """
        Extracts photo chunks from frames list

        path - base path to file that will be reconstructed from parts
        frames - frames list
        correlation_ids - list of correlation ids that will be parsed

        Only FileSendSuccess frames with matching correlation id are saved

        Two files will be generated:
        '<path>.jpg' - decoded photo
        '<path>.raw' - raw photo data (with CAM headers inside)
        """
        parse_and_save_photo_chunks(path + '.jpg', frames, correlation_ids)
        parse_and_save_file_chunks(path + '.raw', frames, correlation_ids)

    def extract_and_save_beacons(path, frames):
        """
        Extracts beacon frames, parses them and dumps to file

        path - path to file that will be reconstructed from parts
        frames - frames list

        Only BeaconFrame frames are parsed
        
        NOTE: This function WILL NOT parse beacons retrieved from telemetry.curent/telemetry.previous files
        """
        from tools.parse_beacon import ParseBeacon
        import json

        beacons = map(ParseBeacon.parse, frames)
        beacons = filter(lambda x: x is not None, beacons)

        with open(path, 'w') as f:
            json.dump(beacons, f, default=ParseBeacon.convert_values, sort_keys=True, indent=4)

    def extract_and_save_file_list(path, frames, correlation_id):
        """
        Extracts file list frames, parses them and dumps to file

        path - path to file that will be reconstructed from parts
        frames - frames list
        correlation_id - single correlation id that will be parsed

        Only BeaconFrame frames are parsed
        
        NOTE: This function WILL NOT parse beacons retrieved from telemetry.curent/telemetry.previous files
        """
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
        'extract_and_save_file_chunks': extract_and_save_file_chunks,
        'extract_and_save_photo_chunks': extract_and_save_photo_chunks,
        'extract_and_save_raw_and_photo': extract_and_save_raw_and_photo,
        'extract_and_save_beacons': extract_and_save_beacons,
        'extract_and_save_file_list': extract_and_save_file_list
    }