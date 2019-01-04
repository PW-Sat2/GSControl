import os

import numpy as np

from summary.mission_store import MissionStore
from summary.steps_lib.files import get_downloaded_files


class MissingFilesTasklistGenerator:
    @staticmethod
    def _generateTelecommandData(missing_files, max_chunks, cid_start):
        def splitAllChunks(data):
            splitCount = (len(data) / max_chunks) + 1
            return map(lambda x: list(x), np.array_split(data, splitCount))

        missingSplittedChunksPerFile = map(lambda (name, info): ({
            "name": name,
            "chunks": splitAllChunks(info["MissingChunks"])
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


if __name__ == '__main__':
    import argparse


    def parse_args():
        default_mission_repository = os.path.abspath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../mission'))

        parser = argparse.ArgumentParser()

        parser.add_argument('-s', '--session', required=True,
                            help="Session number", type=int)
        parser.add_argument('-m', '--mission-path', required=False,
                            help="Path to mission repository", default=default_mission_repository)
        parser.add_argument('-c', '--max-chunks', required=False,
                            help="Maximum chunks allowed for download with single telecommand", default=20, type=int)
        parser.add_argument('-o', '--output', required=False,
                            help="Output file path", default='tasklist.missings.py')
        parser.add_argument('-i', '--cid-start', required=False,
                            help="Beginning of generated correlation id", default=30, type=int)

        return parser.parse_args()


    def main(args):
        store = MissionStore(root=args.mission_path)
        session = store.get_session(args.session)

        telecommandsText = MissingFilesTasklistGenerator.generate(session, args.max_chunks, args.cid_start)

        output_file = open(args.output, 'w')
        output_file.write(telecommandsText)
        output_file.flush()
        output_file.close()


    main(parse_args())
