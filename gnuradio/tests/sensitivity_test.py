# usage:
# 1) connect pluto sdr with funcube with 60 dB attenuators
# 2) adjust parameters below
# 3) run ths piece of software

attenuation_range = [66.2, 68]
attenuation_step = 0.2
frequency = 435303500

frames_on_each_attenuation = 50

filename = "/home/gregg/pwsat/1200_10.wav"

frames_in_wav = 10


import os, subprocess, time, numpy

os.system('rm downlink_frames results_file')
os.system('touch downlink_frames')
os.system('grcc iq_to_pluto_params.grc -d .')
os.system('grcc ../downlink/downlink.grc -d .')
os.system('grcc ../downlink/source/funcube_source.grc -d .')


subprocess.Popen("./downlink.py")
subprocess.Popen("./funcube_source.py")

def get_frames():
    return sum(1 for line in open('downlink_frames', 'r'))

results = []

results_file_ = open('results_file', 'w')

time.sleep(3)

for att in numpy.arange(attenuation_range[0], attenuation_range[1]+attenuation_step, attenuation_step):
    print("Attenuation {}".format(att))

    start = get_frames()
    for i in range(0, frames_on_each_attenuation/frames_in_wav):
        os.system("./iq_to_pluto_params.py -f {} -a {} --file {}".format(frequency, att, filename))
    time.sleep(1)
    end = get_frames()

    results.append([att, end-start])
    results_file_.write("{} {}\n".format(att, end-start))
    results_file_.flush()
    print("{} {}".format(att, end-start))
    
print(results)

results_file_.close()