from bench_init import *

import pprint

from tools.remote_files import RemoteFileTools

# Request info about particular file
chosen_file = send(tc.fs.GetFileInfo('/', 'telemetry.current'))
pprint.pprint(chosen_file)

# Download file
chunks = send(tc.fs.DownloadFile(chosen_file["File"], chosen_file["Chunks"]))

# Save file
RemoteFileTools.save_chunks('downloaded.raw', chunks)
