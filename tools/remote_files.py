import random
import re
from math import ceil
import struct
from utils import ensure_string

from response_frames import common, file_system
from telecommand import *
import time


class RemoteFile:
    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver
    def download(self, file_to_download, correlation_id = None, max_chunks_at_once = 20):
        if correlation_id is None:
            correlation_id = random.randrange(0, 255, 1)
        chunks_qty = file_to_download['Chunks']
        file_chunks = [x for x in range(0, chunks_qty)]
        remaining = [x for x in range(0, chunks_qty)]
        while len(remaining) > 0:
            if max_chunks_at_once > len(remaining):
                request_qty = len(remaining)
            else:
                request_qty = max_chunks_at_once
            try:
                self.sender.send(DownloadFile(file_to_download['File'], correlation_id, [remaining[i] for i in range(request_qty)]))
            except:
                print("Exception in sender")
            rcv_counter = 0
            
            while rcv_counter < request_qty:
                try:
                    recv = self.receiver.receive_frame()
                except:
                    print("Exception in receive!")
                rcv_counter += 1
                if isinstance(recv, common.FileSendSuccessFrame):
                    if (recv.correlation_id == correlation_id):
                        file_chunks[recv.seq()] = recv.response
                        try:
                            remaining.remove(recv.seq())
                            pass
                        except:
                            pass
                        print("Got {}/{}".format(recv.seq() + 1, chunks_qty))
                    else:
                        print("Wrong correlation id: {}/{}".format(recv.correlation_id, correlation_id))
            else:
                print("Not response frame or error response frame")
        return file_chunks
        
        
    def download_legacy(self, file_to_download, correlation_id = None):
        if correlation_id is None:
            correlation_id = random.randrange(0, 255, 1)
        chunks_qty = file_to_download['Chunks']
        file_chunks = [x for x in range(0, chunks_qty)]
        remaining = [x for x in range(0, chunks_qty)]
        while len(remaining) > 0:
            self.sender.send(DownloadFile(file_to_download['File'], correlation_id, [remaining[0]]))
            recv = self.receiver.receive_frame()
            if isinstance(recv, common.FileSendSuccessFrame):
                if (recv.correlation_id == correlation_id):
                    file_chunks[recv.seq()] = recv.response
                    try:
                        remaining.remove(recv.seq())
                        pass
                    except:
                        pass
                    print("Got {}/{}".format(recv.seq() + 1, chunks_qty))
                else:
                    print("Wrong correlation id: {}/{}".format(recv.correlation_id, correlation_id))
            else:
                print("Not response frame or error response frame")
        return file_chunks


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
