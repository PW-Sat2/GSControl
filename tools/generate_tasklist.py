import os
import sys
import glob

import numpy as np
import datetime as dt

import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from summary.mission_store import MissionStore
from summary.steps_lib.files import get_downloaded_files

import telecommand

class ChunksEstimation:
    def __str__(self):
        return "current start: {0}, current end: {1}, previous_start: {2}, previous_end: {3}".format(            
            self.current_start,
            self.current_end,
            self.previous_start,
            self.previous_end)


def flat_array(arr):
    return [y for x in arr for y in x]

def splitAllChunks(data, max_chunks):
    splitCount = (len(data) / max_chunks) + 1
    return map(lambda x: list(x), np.array_split(data, splitCount))

def pop_matching(arr, total, delegate):
    taken = []
    idx = 0
    while True:    
        if (len(taken) >= total) or (idx >= len(arr)):
            break;

        val = arr[idx]

        if delegate(val):
            taken.append(val)
            del arr[idx]
        else:
            idx = idx + 1

    return taken

def read_session_list_files(session):
    # get newest list files
    file_list_paths = sorted(glob.glob(session.expand_artifact_path('file_list*')), key=os.path.basename, reverse=True)
    
    if len(file_list_paths) == 0:
        raise Exception("No file list in session {}".format(session.session_number))

    all_files = []

    for files in file_list_paths:
        file_list_txt = session.read_artifact(files)
        loaded_list = json.loads(file_list_txt.replace("'", '"'))

        for file in loaded_list:
            # if file not in all_files, add it
            if len(filter(lambda x: x['File'] == file['File'], all_files)) == 0:
                all_files.append(file)

    return all_files

def generate_missings_from_session(session):
    missing = session.read_artifact(session.expand_artifact_path('tasklist.missing.py'))
    return missing.replace('\r', '').replace('\t', '').replace(',\n', '\n').split('\n')[1:-1]

def get_latest_file_list(store):
    def to_session_nr(name):
        try:
            return int(os.path.basename(name))
        except ValueError:
            return 0

    f = glob.glob(store.root + "/sessions/*")
    session_nrs = [to_session_nr(i) for i in glob.glob(store.root + "/sessions/*")]
    session_nrs = sorted(session_nrs, reverse=True)
    for session in session_nrs:
        try:
            return read_session_list_files(store.get_session(session))
        except:
            continue
    return {}

def generate_download_files_tasks(mission_store, files_to_download, chunks_per_tc, cid_start):
    file_list = get_latest_file_list(mission_store)

    cid = cid_start

    tasklist = []

    for file in files_to_download:
        file_description = filter(lambda x: x['File'] == file, file_list)
        if len(file_description) != 1:
            raise Exception("Cannot find description of file {}".format(file))
        file_description = file_description[0]

        chunks_all = splitAllChunks(range(0, file_description["Chunks"]), chunks_per_tc)

        for chunks in chunks_all:
            tasklist.append(MissingFilesTasklistGenerator._generateTelecommandText({
                "cid": cid,
                "chunks": ', '.join(map(str, chunks)),
                "file": file
            }))
            cid += 1

    return tasklist

def generate_remove_files_tasks(mission_store, files_to_delete, cid_start):
    cid = cid_start
    tasklist = []
    file_list = get_latest_file_list(mission_store)

    for file in files_to_delete:
        if filter(lambda x: x['File'] == file, file_list) == []:
            print "WARNING: File {} not found in last file list!".format(file)

        tasklist.append("[tc.RemoveFile({}, \'{}\'), Send, WaitMode.Wait]".format(
            cid,
            file))
        cid += 1

    tasklist.append("[tc.ListFiles({}, '/'), Send, WaitMode.Wait]".format(cid))
    cid += 1
    return tasklist

class MissingFilesTasklistGenerator:
    @staticmethod
    def _generateTelecommandData(missing_files, max_chunks, cid_start):
        missingSplittedChunksPerFile = map(lambda (name, info): ({
            "name": name,
            "chunks": splitAllChunks(info["MissingChunks"], max_chunks)
        }), missing_files.items())

        flattenedChunksPerFile = [{"name": x["name"], "chunks": y} for x in missingSplittedChunksPerFile for y in
                                  x["chunks"]]

        telecommandData = map(lambda (i, x): ({
            "cid": i + cid_start,
            "chunks": ', '.join(map(str, x["chunks"])),
            "file": x["name"]
        }), enumerate(flattenedChunksPerFile))

        return telecommandData

    @staticmethod
    def _generateTelecommandText(singleTelecommandData):
        return "[tc.DownloadFile({0}, '/{1}', [{2}]), Send, WaitMode.Wait]".format(
            singleTelecommandData["cid"],
            singleTelecommandData["file"],
            singleTelecommandData["chunks"]
        )

    @staticmethod
    def _filter_missing(files):
        result = {}

        for name, info in files.items():
            if info['MissingChunks']:
                result[name] = info

        return result

    @staticmethod
    def generate(session, max_chunks, cid_start):
        downloaded_files = get_downloaded_files(session.tasklist, session.all_frames)

        missing_files = MissingFilesTasklistGenerator._filter_missing(downloaded_files)

        telecommandData = MissingFilesTasklistGenerator._generateTelecommandData(missing_files, max_chunks, cid_start)
        telecommandsText = ",\r\n\t".join(
            map(lambda x: MissingFilesTasklistGenerator._generateTelecommandText(x), telecommandData))

        return 'tasks = [\r\n' + telecommandsText + '\r\n]'



class NextSessionTelemetryTasklistGenerator:
    CHUNKS_PER_MINUTE = 1.82
    MAX_CHUNKS = 2280
    CHUNKS_SAFE_BUFFER = 50

    def estimateChunks(self, startChunk, startTime, nextTime):
        chunksPerMinute = self.CHUNKS_PER_MINUTE

        estimation = ChunksEstimation()
        estimation.current_start = startChunk
        estimation.previous_start = -1
        estimation.previous_end = -1
        
        totalSeconds = (nextTime - startTime).total_seconds();

        estimation.generated_chunks = int((totalSeconds / 60) * chunksPerMinute) + self.CHUNKS_SAFE_BUFFER

        estimation.current_end = estimation.current_start + estimation.generated_chunks

        if (estimation.current_end > self.MAX_CHUNKS):
            estimation.previous_start = estimation.current_start
            estimation.previous_end = self.MAX_CHUNKS
            estimation.current_start = 0
            estimation.current_end -= self.MAX_CHUNKS

        return estimation


    def read_session_telemetry_chunks(self, session):
        files = read_session_list_files(session)

        telemetry_entries = filter(lambda x: x["File"] == 'telemetry.current', files)
        return telemetry_entries[0]["Chunks"]

    def estimate_session(self, previous_session, next_session_start):
        start_time = previous_session.read_metadata()["start_time_iso_with_zone"]
        start_chunk = self.read_session_telemetry_chunks(previous_session)

        if start_chunk is None:
            print "Unable to find previous session file list"
            return
        

        return self.estimateChunks(
            startChunk=start_chunk, 
            startTime=start_time, 
            nextTime=next_session_start
        )


    def generate_telemetry_tasks(self, estimation, density_level = 5, chunk_step = 50, cid_start = 30, chunks_per_tc = 20):
        
        # Generate the start indexes with binary division of the range, so that telemetry gets more dense as more chunks are downloaded
        indexes = [0, chunk_step/2]
        for current_level in range(2, density_level, 1):
            divisor = max(1, int(chunk_step/(2**current_level))) 
            indexes = indexes + flat_array([[index-divisor, index+divisor] for index in indexes[-(2**(current_level-2)):]])
            if divisor == 1:
                break;

        chunks_offsets = map(lambda start: range(start, estimation.generated_chunks, chunk_step) ,indexes)
        chunk_index_offset = -estimation.current_start if estimation.previous_end == -1 else  estimation.previous_end - estimation.previous_start

        chunk_ids = flat_array(map(lambda x: map(lambda y: y - chunk_index_offset, x), chunks_offsets))

        if max(chunk_ids) >= self.MAX_CHUNKS:
            print 'ERROR: Telemetry is out of range, session period is to large'
            return []

        telemetry_chunks = []
        while len(chunk_ids) > 0:
            if chunk_ids[0] < 0:
                telemetry_chunks.append({
                    "name": "telemetry.previous",
                    "chunks": [x+self.MAX_CHUNKS for x in pop_matching(chunk_ids, chunks_per_tc, lambda x: x < 0)]
                })
            else:
                telemetry_chunks.append({
                    "name": "telemetry.current",
                    "chunks": pop_matching(chunk_ids, chunks_per_tc, lambda x: x >= 0)
                })

        telecommandData = map(lambda (i, x): ({
            "cid": i + cid_start,
            "chunks": ', '.join(map(str, x["chunks"])),
            "file": x["name"]
        }), enumerate(telemetry_chunks))

        return map(lambda x: MissingFilesTasklistGenerator._generateTelecommandText(x), telecommandData)


if __name__ == '__main__':  
    import argparse
    
    def parse_args():
        default_mission_repository = os.path.abspath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../mission'))

        task_templates_path = os.path.abspath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tasklist_templates'))

        default_template_path = os.path.join(task_templates_path, 'telemetry_download.template')

        parser = argparse.ArgumentParser()

        parser.add_argument('-s', '--start-session', required=False,
                            help="Start session number", type=int)
        parser.add_argument('-e', '--end-session', required=False,
                            help="End session number. Start session + 1 if omitted", type=int, default=0)
        parser.add_argument('-m', '--mission-path', required=False,
                            help="Path to mission repository", default=default_mission_repository)
        parser.add_argument('-c', '--chunks-per-tc', required=False,
                            help="Maximum chunks allowed for download with single telecommand", default=20, type=int)
        parser.add_argument('-o', '--output', required=False,
                            help="Output file path", default='tasklist.telemetry.py')
        parser.add_argument('-i', '--cid-start', required=False,
                            help="Beginning of generated correlation id", default=30, type=int)
        parser.add_argument('-t', '--template-path', required=False,
                            help="Path to template of the tasklist", type=str, default=default_template_path)
        parser.add_argument('-f', '--files-to-download', nargs='+', default=[],
                            help="Files to download.")
        parser.add_argument('-d', '--files-to-delete', nargs='+', default=[],
                            help="Files to delete.")
        parser.add_argument('-r', '--missings', action='store_true',
                            help="Get missing tasklist from previous session")

        return parser.parse_args()

    def main(args):

        format_args = [
            dt.datetime.now(),
        ]

        if args.start_session is not None:
            end_session = args.end_session if args.end_session > 0 else args.start_session + 1
            store = MissionStore(root=args.mission_path)
            start_session_view = store.get_session(args.start_session)
            end_session_view = store.get_session(end_session)
            correlation_id = args.cid_start
            task_generator = NextSessionTelemetryTasklistGenerator()
            estimation = task_generator.estimate_session(
                start_session_view, 
                end_session_view.read_metadata()["start_time_iso_with_zone"])

            if args.missings:
                missings = generate_missings_from_session(store.get_session(end_session - 1))
                correlation_id += len(missings)
                print "Generated missings!"
                generated_tasks_missings = ",\n    ".join(missings) + ','
            else:
                generated_tasks_missings = ""

            if not (estimation is None):
                generated_tasks = task_generator.generate_telemetry_tasks(
                    estimation, 
                    density_level=4, 
                        chunks_per_tc=args.chunks_per_tc,
                    cid_start=correlation_id
                    )
                correlation_id += len(generated_tasks)
                generated_tasks_string = ",\n    ".join(generated_tasks) + ','
            else:
                generated_tasks = []
                generated_tasks_string = ""

            if args.files_to_download != []:
                print "Downloading files: {}".format(args.files_to_download)
                generated_file_download_tasks = generate_download_files_tasks(store, args.files_to_download, args.chunks_per_tc, correlation_id)
                correlation_id += len(generated_file_download_tasks)
                generated_file_download_tasks_string = ",\n    ".join(generated_file_download_tasks) + ','
            else:
                generated_file_download_tasks = []
                generated_file_download_tasks_string = ""
            
            if args.files_to_delete != []:
                print "Removing files: {}".format(args.files_to_delete)
                remove_file_tasks = generate_remove_files_tasks(store, args.files_to_delete, correlation_id)
                correlation_id += len(remove_file_tasks)
                remove_file_tasks_string = ",\n    ".join(remove_file_tasks) + ','
            else:
                remove_file_tasks = []
                remove_file_tasks_string = ""

            format_args.extend([
                args.start_session,
                end_session,
                end_session_view.read_metadata()["start_time_iso_with_zone"],
                generated_tasks_string,
                generated_tasks_missings,
                generated_file_download_tasks_string,
                remove_file_tasks_string,
            ])
        else:
            generated_tasks = ''
            
        with open(args.template_path, 'r') as template:
            output_file = open(args.output, 'w')
            
            output_file.write(template.read().format(*format_args))
            output_file.flush()
            output_file.close()


    main(parse_args())
