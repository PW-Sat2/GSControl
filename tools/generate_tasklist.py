import os
import numpy as np

from summary.mission_store import MissionStore
import telecommand

class MissingFilesTasklistGenerator:
    @staticmethod
    def _getAllSessionFilePaths(session):
        downloadFiles =  filter(lambda x: isinstance(x[0], telecommand.fs.DownloadFile), session.tasklist)
        allFiles = map(lambda x: x[0]._path, downloadFiles)

        return allFiles
    
    @staticmethod
    def _readMissingChunksPerFile(allFiles):
        allPossibleMissingFiles = map(lambda x: (x+'.missing').strip('/'), allFiles)
        allPossibleMissingFiles = list(set(allPossibleMissingFiles))
        allExistingMissingFiles = filter(lambda x: session.has_artifact(x), allPossibleMissingFiles)

        def readChunksFromMissing(file):
            return session.read_artifact(file, as_lines=True)[0].strip('[],').split()

        missingChunksPerFile = map(lambda x: ({"name": x.replace('.missing',''), "data": readChunksFromMissing(x)}), allExistingMissingFiles)
        return missingChunksPerFile

    @staticmethod
    def _generateTelecommandData(missingChunksPerFile, max_chunks, cid_start):    
        def splitAllChunks(data):
            splitCount = (len(data)/max_chunks)+1
            return map(lambda x: list(x), np.array_split(data,splitCount))

        missingSplittedChunksPerFile = map(lambda x: ({
            "name": x["name"],
            "chunks": splitAllChunks(x["data"])
        }) , missingChunksPerFile)


        flattenedChunksPerFile = [{"name": x["name"], "chunks": y} for x in missingSplittedChunksPerFile for y in x["chunks"]]

        telecommandData = map(lambda (i,x): ({
            "cid": i+cid_start,
            "chunks": ''.join(x["chunks"]),
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
    def generate(session, max_chunks, cid_start):
        allFiles = MissingFilesTasklistGenerator._getAllSessionFilePaths(session)
        missingChunksPerFile = MissingFilesTasklistGenerator._readMissingChunksPerFile(allFiles)
        telecommandData = MissingFilesTasklistGenerator._generateTelecommandData(missingChunksPerFile, max_chunks, cid_start)
        telecommandsText = ",\r\n\t".join(map(lambda x: MissingFilesTasklistGenerator._generateTelecommandText(x), telecommandData))

        return telecommandsText

if __name__ == '__main__':
    import argparse

    default_mission_repository = mission_data = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../mission'))

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--session', required=True,
                        help="Session number", type=int)
    parser.add_argument('-m', '--mission-path', required=False,
                        help="Path to mission repository", default=default_mission_repository)
    parser.add_argument('-c', '--max-chunks', required=False,
                        help="Maximum chunks allowed for download with single telecommand", default=20, type=int)
    parser.add_argument('-o', '--output', required=False,
                        help="Output file path", default='tasklist.missings.py')
    parser.add_argument('-v', '--uplink-port', required=False,
                        help="Uplink port", default=7000, type=int)
    parser.add_argument('-i', '--cid-start', required=False,
                        help="Beginning of generated correlation id", default=30, type=int)
            

    args = parser.parse_args()

    mission_data = default_mission_repository
    store = MissionStore(root=args.mission_path)
    session = store.get_session(args.session)

    telecommandsText = MissingFilesTasklistGenerator.generate(session, args.max_chunks, args.cid_start)

    output_file = open(args.output, 'w')
    output_file.write('tasks = [\r\n' + telecommandsText + '\r\n]')
    output_file.flush()
    output_file.close()
