prefix = '/home/gregg/mnt/E/iq/iq_'
sufix = ".iq"
att = [
# '74.5',
# '74.0',
# '73.5',
# '73.0',
# '72.5',
# '72.0',
# '71.5',
# '71.0',
# '70.5',
# '70.0',
# '69.5',
'69.0',
'68.5',
'68.0',
'67.5',
'67.0',
'66.5',
'66.0',
'65.5',
'65.0'
]

import os, subprocess, time, numpy

os.system('rm downlink_frames results_file -f')
os.system('grcc downlink.grc -d .')
fp = open(os.devnull, 'w')


param = 0.1


def get_frames():
    return sum(1 for line in open('downlink_frames', 'r'))

results = []

results_file_ = open('results_file', 'w')


for now in att:
    filename = prefix + now + sufix
    now = float(now)
    os.system('rm downlink_frames -f')

    subprocess.Popen(["./downlink.py", "-f", filename, "-p", str(param)], stdout=fp)
    time.sleep(15)

    os.system("ps aux | grep -ie \"downlink.py\" | awk '{print $2}' | xargs kill -9 >> /dev/null 2>> /dev/null")

    frames = get_frames()

    results.append([now, frames])
    results_file_.write("{} {}\n".format(now, frames))
    results_file_.flush()
    print("{} {}".format(now, frames))
    
print(results)

results_file_.close()

