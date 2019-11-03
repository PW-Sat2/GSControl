from response_frames.common import FileSendSuccessFrame, FileSendErrorFrame

class DownloadFileTask:
    def __init__(self, correlation_id, path, chunks):
        self.correlation_id = correlation_id
        self.path = path
        self.chunks = chunks

    @staticmethod
    def create_from_task(taskitem):
        return DownloadFileTask(taskitem._correlation_id, taskitem._path, taskitem._seqs)

    def length(self):
        return len(self.chunks)
    
    def file_name(self):
        return self.path[1:]

    def to_dict(self):
        return {
            "correlation_id" : self.correlation_id,
            "path" : self.path,
            "chunks" : self.chunks
        }

    @staticmethod
    def from_dict(fields):
        try:
            return DownloadFileTask(fields["correlation_id"], str(fields["path"]), fields["chunks"])
        except:
            return None


class DownloadFrameView:
    def __init__(self, correlation_id, chunk, is_success):
        self.is_success = is_success
        self.correlation_id = correlation_id
        self.chunk = chunk

    @staticmethod
    def create_from_frame(frame):
        if not DownloadFrameView.is_download_frame(frame):
            return None

        is_success = isinstance(frame, FileSendSuccessFrame)     
        return DownloadFrameView(frame.correlation_id, frame._seq, is_success)

    @staticmethod
    def is_download_frame(frame):
        return type(frame) in [FileSendSuccessFrame, FileSendErrorFrame]
