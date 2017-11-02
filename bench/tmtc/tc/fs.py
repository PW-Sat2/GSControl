import telecommand.fs
import response_frames.file_system
from tools.remote_files import RemoteFileTools
from utils import ensure_string


class ListFiles(object):
    def __init__(self, path):
        self.path = path

    def send(self, tmtc):
        frames = tmtc.send_tc_with_multi_response(telecommand.fs.ListFiles, response_frames.file_system.FileListSuccessFrame, self.path)
        files = []
        for f in frames:
            files.extend(RemoteFileTools.parse_file_list(f))
        return files


class GetFileInfo(object):
    def __init__(self, path, filename):
        self.filename = filename
        self.path = path
        self.lf = ListFiles(path)

    def send(self, tmtc):
        file_list = self.lf.send(tmtc)
        
        try:
            return (item for item in file_list if item["File"] == self.filename).next()
        except StopIteration:
            return None


class RemoveFile(object):
    def __init__(self, path):
        self.path = path

    def send(self):
        response = tmtc.send_tc_with_response(telecommand.fs.RemoveFile, response_frames.common.FileRemoveSuccessFrame, self.path)
        file_removed = ''.join(map(chr, response.payload()[2:]))
        if file_removed != path:
            raise Exception("Incorrect path returned" + file_removed)
        print "File %s removed!" % file_removed


class DownloadFile(object):
    def __init__(self, path, chunks, max_chunks_at_once=20):
        self.path = path
        self.chunks = chunks
        self.max_chunks_at_once = max_chunks_at_once

    def send(self, tmtc):
        file_chunks = [x for x in range(0, self.chunks)]
        remaining = [x for x in range(0, self.chunks)]

        while len(remaining) > 0:
            if self.max_chunks_at_once > len(remaining):
                request_qty = len(remaining)
            else:
                request_qty = self.max_chunks_at_once

            chunks_request_now = [remaining[i] for i in range(request_qty)]
            collected_frames = tmtc.send_tc_with_multi_response(telecommand.fs.DownloadFile, response_frames.common.FileSendSuccessFrame, self.path, chunks_request_now)

            for frame in collected_frames:
                file_chunks[frame.seq()] = frame.response
                try:
                    remaining.remove(frame.seq())
                except:
                    pass
                print("Got {}/{}".format(frame.seq() + 1, self.chunks))
        
        return file_chunks
