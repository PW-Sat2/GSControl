from tools.remote_files import *
from pprint import pprint, pformat

from task_actions import *
from collections import defaultdict

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

    def get_paths_and_cids_from_tasklist(tasklist_path):
        """
        Extracts file paths and their correlation ids dictionary from tasklist

        tasklist_path - path to tasklist file
        """

        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../PWSat2OBC/integration_tests'))

        import telecommand as tc

        with open(tasklist_path) as tasks_file:
            exec(tasks_file) in globals(), locals()
            tasks_file.close()

        files_with_cids = defaultdict(list)
        for task in tasks:
            command = task[0]
            if isinstance(command, tc.DownloadFile):
                argument = task[0]
                correlation_id = command.correlation_id()
                
                payload = command.payload()
                path_length = payload[1]
                path = ''.join(payload[2:(path_length + 2)])

                files_with_cids[path].append(correlation_id)

        return files_with_cids

    def extract_and_save_files_from_tasklist(tasklist_path, target_folder_path, frames):
        """
        Extracts file chunks from frames list based on tasklist

        tasklist_path - path to tasklist file
        target_folder_path - path to folder for files that will be reconstructed from parts
        frames - frames list

        Only FileSendSuccess frames with correlation id matching DownloadFile commands are saved
        """

        files_with_cids = get_paths_and_cids_from_tasklist(tasklist_path)
        for path in files_with_cids:
            cids = files_with_cids[path]

            full_path = target_folder_path + path

            extract_and_save_file_chunks(full_path, frames, cids)
        
    return {
        'extract_and_save_file_chunks': extract_and_save_file_chunks,
        'extract_and_save_photo_chunks': extract_and_save_photo_chunks,
        'extract_and_save_raw_and_photo': extract_and_save_raw_and_photo,
        'extract_and_save_beacons': extract_and_save_beacons,
        'extract_and_save_file_list': extract_and_save_file_list,
        'extract_and_save_files_from_tasklist': extract_and_save_files_from_tasklist
    }