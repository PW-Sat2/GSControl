filename = "/home/gregg/mnt/E/iq/iq_65.0.iq"

import os, subprocess, time, numpy

os.system('rm downlink_frames results_file -f')
os.system('grcc downlink.grc -d .')
fp = open(os.devnull, 'w')


# was 0.045
start = 0.05
stop = 0.2
step = 0.005


def get_frames():
    return sum(1 for line in open('downlink_frames', 'r'))

results = []

results_file_ = open('results_file', 'w')

time.sleep(3)

for now in numpy.arange(start, stop+step, step):
    
    os.system('rm downlink_frames -f')

    subprocess.Popen(["./downlink.py", "-f", filename, "-p", str(now)], stdout=fp)
    time.sleep(11)

    os.system("ps aux | grep -ie \"downlink.py\" | awk '{print $2}' | xargs kill -9 >> /dev/null 2>> /dev/null")

    frames = get_frames()

    results.append([now, frames])
    results_file_.write("{} {}\n".format(now, frames))
    results_file_.flush()
    print("{} {}".format(now, frames))
    
print(results)

results_file_.close()

