from radio_pwsat_pl_common import *

all_frames = download_files()

merge_and_save_bin_beacons(only_unique_packets(all_frames), 'Turbo-Ola.bin')
