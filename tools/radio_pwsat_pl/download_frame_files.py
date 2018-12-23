import sys
from radio_pwsat_pl_common import *

search_timespan = 30
if len(sys.argv) > 1:
    try:
        timespan_parameter = int(sys.argv[1])
        search_timespan = timespan_parameter
    except ValueError:
        pass

all_frames = download_files(True)

# ----- filter by current session -----

timestamp = datetime.utcnow()
# timestamp = datetime.strptime("2018-12-06_09-25-00", '%Y-%m-%d_%H-%M-%S')
all_frames = filter_by_time(all_frames, timestamp, (-search_timespan, 10))

# save frames
save_frames_to_csv(get_elka_frames(all_frames), 'elka_downlink.frames')
save_frames_to_csv(get_fp_frames(all_frames), 'gliwice_downlink.frames')

save_frames_to_csv(only_unique_packets(all_frames), 'all.frames')


# stats
print "Frames:"
print "All:", len(all_frames)
print "Elka:", len(get_elka_frames(all_frames))
print "FP:", len(get_fp_frames(all_frames))
print "Ham radio:", len(get_ham_frames(all_frames))
print ""

all_frames = only_unique_packets(all_frames)

print "Unique frames:", len(all_frames)
print "Elka:", len(get_elka_frames(all_frames))
print "FP (additional to Elka):", len(get_fp_frames(all_frames))
print "Ham radio (additional to Elka + FP):", len(get_ham_frames(all_frames))

all_frames = only_unique_packets(all_frames)
