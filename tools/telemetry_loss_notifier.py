import os
import sys
import glob
import json
import argparse
from slacker import Slacker
import traceback

argparser = argparse.ArgumentParser()
argparser.add_argument('-s', '--start', required=True, type=int,
                help="Start session number")
argparser.add_argument('-n', '--next', required=False, type=int, default=10,
                help="Next sessions to check")
argparser.add_argument('-e', '--elevation', required=False, type=int, default=20,
                help="Min. elevation to show session in the results")
argparser.add_argument('-t', '--token', required=True,
                help="Slack User Token")
argparser.add_argument('-c', '--channel', required=True,
                help="Main garbage channel name")

args = argparser.parse_args()

slack_channel = args.channel
slack_token = args.token

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from summary.mission_store import MissionStore
from summary.steps_lib.files import get_downloaded_files


def notify_oper(text):
    try:
        s = Slacker(slack_token)
        channel_id = s.channels.get_channel_id(slack_channel)
        s.chat.post_message(channel=channel_id, text=text ,parse='full', link_names=1, username="Session")
    except Exception:
        traceback.print_exc()


class NextSessionTelemetryTasklistGenerator:
    CHUNKS_PER_MINUTE = 1.82
    MAX_CHUNKS = 2280
    CHUNKS_SAFE_BUFFER = 50

    def estimateChunks(self, startChunk, startTime, nextTime):
        chunksPerMinute = self.CHUNKS_PER_MINUTE

        current_start = startChunk
        previous_start = -1
        previous_end = -1
        
        totalSeconds = (nextTime - startTime).total_seconds();
        generated_chunks = int((totalSeconds / 60) * chunksPerMinute) + self.CHUNKS_SAFE_BUFFER

        current_end = current_start + generated_chunks
        left = 2*self.MAX_CHUNKS - current_end
        return left

    def read_session_telemetry_chunks(self, session):

        file_list_paths = glob.glob(session.expand_artifact_path('file_list*'))
        
        for file_list_file in file_list_paths:
            loaded_list = []
            
            if session.has_artifact(file_list_file) == False:
                continue

            file_list_txt = session.read_artifact(file_list_file)
            loaded_list = json.loads(file_list_txt.replace("'", '"'))

            telemetry_entries = filter(lambda x: x["File"] == 'telemetry.current', loaded_list)

            if len(telemetry_entries) == 0:
                continue

            return telemetry_entries[0]["Chunks"]

    def estimate_session(self, previous_session, next_session_end):
        start_time = previous_session.read_metadata()["start_time_iso_with_zone"]
        start_chunk = self.read_session_telemetry_chunks(previous_session)
        
        if start_chunk is None:
            print "Unable to find previous session file list"
            return
        

        return self.estimateChunks(
            startChunk=start_chunk, 
            startTime=start_time, 
            nextTime=next_session_end
        )


default_mission_repository = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../mission'))
path_to_sessions = default_mission_repository + "/sessions"

list_of_directories = [name for name in os.listdir(path_to_sessions) if os.path.isdir(os.path.join(path_to_sessions, name))]

store = MissionStore(root=default_mission_repository)
start_session_view = store.get_session(args.start)

future = NextSessionTelemetryTasklistGenerator()

message = "*Telemetry.current/previous chunks margin since session {}:*\n".format(args.start)

for i in range(args.start + 1, args.start + args.next + 1):
    try:
        list_of_directories.index(str(i))
        end_session_view = store.get_session(i)
        estimation = future.estimate_session(
            start_session_view,
            end_session_view.read_metadata()["stop_time_iso_with_zone"])

        if end_session_view.read_metadata()["maximum_elevation"] > args.elevation:
            line = ""
            
            if estimation < 0:
                line = "> :x: ~session {}: margin~ *{:5}*\t~({}, elev. {} deg)~".format(i, estimation, end_session_view.read_metadata()["start_time_iso_with_zone"], end_session_view.read_metadata()["maximum_elevation"])
            elif estimation < future.CHUNKS_SAFE_BUFFER:
                line = "> :warning: ~session {}: margin~ *{:5}*\t~({}, elev. {} deg)~".format(i, estimation, end_session_view.read_metadata()["start_time_iso_with_zone"], end_session_view.read_metadata()["maximum_elevation"])
            else:
                line = "> :heavy_check_mark: session {}: margin *{:5}*\t({}, elev. {} deg)".format(i, estimation, end_session_view.read_metadata()["start_time_iso_with_zone"], end_session_view.read_metadata()["maximum_elevation"])
                
            message += line + "\n"
    except Exception:
        pass

print(message)

# show only after manual sessions (manual sesion => telemetry download)
if start_session_view.read_metadata()["status"] == "success" or start_session_view.read_metadata()["status"] == "planned":
    notify_oper(message)