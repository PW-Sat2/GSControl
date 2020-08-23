from math import ceil, floor

from response_frames.common import FileSendSuccessFrame, FileSendErrorFrame
from response_frames.memory import MemoryContent
from response_frames.file_system import FileListSuccessFrame
from response_frames.program_upload import EntryProgramPartWriteSuccess

class DownloadFileTask:
    def __init__(self, correlation_id, path, chunks, index= 0):
        self.correlation_id = correlation_id
        self.path = path
        self.chunks = chunks
        self.index = index

    @staticmethod
    def create_from_task(taskitem, index= 0):
        return DownloadFileTask(taskitem._correlation_id, taskitem._path, taskitem._seqs, index)

    def length(self):
        return len(self.chunks)
    
    def file_name(self):
        return self.path[1:]

    def to_dict(self):
        return {
            "index" : self.index,
            "correlation_id" : self.correlation_id,
            "path" : self.path,
            "chunks" : self.chunks
        }

    @staticmethod
    def from_dict(fields):
        try:
            return DownloadFileTask(fields["correlation_id"], str(fields["path"]), fields["chunks"], fields["index"])
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


class MemoryFrameView:
    def __init__(self, correlation_id, sequence_number):
        self.correlation_id = correlation_id
        self.chunk = sequence_number
        self.is_success = True  # used by GUI

    @staticmethod
    def create_from_frame(frame):
        if not MemoryFrameView.is_memory_frame(frame):
            return None
   
        return MemoryFrameView(frame.payload()[0], frame.seq())

    @staticmethod
    def is_memory_frame(frame):
        return type(frame) == MemoryContent


class MemoryTask:
    MaxDownlinkFrameSize = 235
    HeaderSize = 3
    MaxFramePayloadSize = MaxDownlinkFrameSize - HeaderSize
    MaxMemoryTaskPayloadSize = MaxFramePayloadSize - 1

    def __init__(self, correlation_id, offset, size, index= 0):
        self.correlation_id = correlation_id
        self.offset = offset
        self.size = size
        size_framed = int(ceil(float(size) / MemoryTask.MaxMemoryTaskPayloadSize))
        self.chunks = range(0, size_framed)
        self.index = index

    @staticmethod
    def create_from_task(taskitem, index= 0):
        return MemoryTask(taskitem._correlation_id, taskitem.offset, taskitem.size, index)

    def length(self):
        return len(self.chunks)

    def file_name(self):
        return '0x{:x}'.format(self.offset)


class FileListFrameView:
    def __init__(self, correlation_id, sequence_number, file_list):
        self.correlation_id = correlation_id
        self.chunk = sequence_number
        self.is_success = True  # used by GUI
        self.file_list = {}
        for file in file_list:
            file_name = file[0]
            size = file[1]
            chunks = int(ceil(size/230.))
            self.file_list[file_name] = chunks

    @staticmethod
    def create_from_frame(frame):
        if not FileListFrameView.is_file_list_frame(frame):
            return None
   
        return FileListFrameView(frame.payload()[0], frame.seq(), frame.file_list)

    @staticmethod
    def is_file_list_frame(frame):
        return type(frame) == FileListSuccessFrame

class WriteProgramPartTask:
    MaxUplinkPayload = 200 - 5
    MaxProgramPartSize = MaxUplinkPayload - 5

    def __init__(self, entries, offset, content, index= 0):
        self.block_number = int(floor(float(offset) / WriteProgramPartTask.MaxProgramPartSize))
        self.correlation_id = self.block_number
        self.offset = offset
        self.content_length = len(content)
        self.chunks = []
        self.index = index

    @staticmethod
    def create_from_task(taskitem, index= 0):
        return WriteProgramPartTask(taskitem._entries, taskitem._offset, taskitem._content, index)

    @staticmethod
    def generate_dummy_correlation_id(block_number):
        return 1000 + block_number

    def length(self):
        return self.block_number

    def file_name(self):
        return 'UPLOAD: 0x{:x}'.format(self.offset)

    def get_dummy_correlation_id(self):
        return WriteProgramPartTask.generate_dummy_correlation_id(self.block_number)


class WriteProgramPartSuccessFrameView:
    def __init__(self, offset, sequence_number, entries, size):
        self.offset = offset
        self.size = size
        self.entries = entries
        self.block_number = int(floor(float(offset) / WriteProgramPartTask.MaxProgramPartSize))
        self.correlation_id = WriteProgramPartTask.generate_dummy_correlation_id(self.block_number)
        self.chunk = self.block_number
        self.is_success = True  # used by GUI

    @staticmethod
    def create_from_frame(frame):
        if not WriteProgramPartSuccessFrameView.is_write_program_frame(frame):
            return None
   
        return WriteProgramPartSuccessFrameView(frame.offset, frame.seq(), frame.entries, frame.size)

    @staticmethod
    def is_write_program_frame(frame):
        return type(frame) == EntryProgramPartWriteSuccess