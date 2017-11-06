import telecommand.fs
import response_frames.file_system


class ListFiles(object):
    def __init__(self, path):
        self.path = path

    def send(self, tmtc):
        frames = tmtc.send_tc_with_multi_response(telecommand.fs.ListFiles,
                                                  response_frames.file_system.FileListSuccessFrame,
                                                  self.path)
        return frames


class RemoveFile(object):
    def __init__(self, path):
        self.path = path

    def send(self, tmtc):
        response = tmtc.send_tc_with_response(telecommand.fs.RemoveFile,
                                              response_frames.common.FileRemoveSuccessFrame,
                                              self.path,
                                              timeout=50)
        file_removed = ''.join(map(chr, response.payload()[2:]))
        if file_removed != self.path:
            raise Exception("Incorrect path returned" + file_removed)


class DownloadFile(object):
    def __init__(self, path, chunks):
        self.path = path
        self.chunks = chunks

    def send(self, tmtc):
        collected_frames = tmtc.send_tc_with_multi_response(telecommand.fs.DownloadFile,
                                                            response_frames.common.FileSendSuccessFrame,
                                                            self.path,
                                                            self.chunks)
        return collected_frames
