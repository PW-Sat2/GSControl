import random
import re
from math import ceil
import struct
from utils import ensure_string

from response_frames import common, file_system
from telecommand import *
import time

class RemoteFileTools:
    @staticmethod
    def parse_file_list(frame):
        if isinstance(frame, file_system.FileListSuccessFrame):
            res = bytearray(frame.payload())[2:]

            file_list = []
            
            while True:
                now = res.find('\x00')
                if now == -1:
                    return file_list
                
                name = str(res[:now])
                size = struct.unpack('<I', res[now+1:now+5])[0]
                chunks = int(ceil(size/230.))

                file_list.append({'File': name, 'Size': size, 'Chunks': chunks})
                res = res[now+5:]
        else:
            file_list = None

        return file_list


    @staticmethod
    def merge_chunks(chunks):
        data_string = ""
        for i in chunks:
            data_string += ensure_string(i)

        return data_string

    @staticmethod
    def save_chunks(path, chunks):
        data_string = ""
        for i in chunks:
            data_string += ensure_string(i)
        
        with open(path, 'wb') as f:
            f.write(data_string)
            f.close()

    @staticmethod
    def save_photo(path, chunks):
        data_string = ""
        for i in chunks:
            data_string += ensure_string(i)
        data_string = data_string[4:]
        result = ""
        
        while len(data_string) > 0:
            part = data_string[0:512 - 6]
            result += part
            data_string = data_string[512:]
            data_string = data_string[0:]
        
        with open(path, 'wb') as f:
            f.write(result)
            f.close()
