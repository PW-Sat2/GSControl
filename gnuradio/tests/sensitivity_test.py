# usage:
# 1) connect pluto sdr with funcube with 60 dB attenuators
# 2) adjust parameters below
# 3) run ths piece of software

# hardware step is 0.25 dB

<<<<<<< HEAD
attenuation_range = [20, 20]
attenuation_step = 5
frequency = 435275000-2800

frames_on_each_attenuation = 200

filename = "/home/gregg/pwsat/1200_1.iq"
noise_file = "/home/gregg/pwsat/noise.iq"
=======
attenuation_range = [65.5, 68.5]
attenuation_step = 0.5
frequency = 435275000-2500

frames_on_each_attenuation = 100
frames_in_one_file_block = 100
>>>>>>> 2d5a99e... --wip-- [skip ci]

filename = "/home/gregg/pwsat/1200_1.iq"
noise_file = "/home/gregg/pwsat/noise.iq"

assert frames_on_each_attenuation % frames_on_each_attenuation == 0
assert float(attenuation_range[0]/0.25).is_integer()
assert float(attenuation_step/0.25).is_integer()

import os, subprocess, time, numpy
import scikits.audiolab, scipy

folder = '/Ext_Disk'

os.system('rm downlink_frames results_file')
os.system('touch downlink_frames')
os.system('grcc iq_to_usrp_params.grc -d .')
os.system('grcc ../downlink/downlink.grc -d .')
os.system('grcc ../downlink/source/funcube_source.grc -d .')
os.system('mkdir {}/iq'.format(folder))

fp = open(os.devnull, 'w')

subprocess.Popen("./downlink.py", stdout=fp)

def get_frames():
    return sum(1 for line in open('downlink_frames', 'r'))

results = []

results_file_ = open('results_file', 'w')

time.sleep(3)

os.system("rm {}/file.iq".format(folder))
for i in range(0, 2):
    os.system("cat {} >> {}/file.iq".format(noise_file, folder))

for i in range(0, frames_in_one_file_block):
    os.system("cat {} >> {}/file.iq".format(filename, folder))
    os.system("cat {} >> {}/file.iq".format(noise_file, folder))

for att in numpy.arange(attenuation_range[0], attenuation_range[1]+attenuation_step, attenuation_step):
    print("Attenuation {}".format(att))

    subprocess.Popen("./funcube_source.py")

    time.sleep(5)

    start = get_frames()

    for i in range(0, frames_on_each_attenuation/frames_in_one_file_block):
        os.system("./iq_to_pluto_params.py -f {} -a {} --file {}/file.iq".format(frequency, att, folder))

    time.sleep(5)
    end = get_frames()

    results.append([att, end-start])
    results_file_.write("{} {}\n".format(att, end-start))
    results_file_.flush()
    print("{} {}".format(att, end-start))

    os.system("ps aux | grep -ie \"funcube_source.py\" | awk '{print $2}' | xargs kill -9")

    time.sleep(10)

    os.system("mv iq_data_from_current_session_after_doppler_correction " + folder + "/iq/iq_" + str(att) + ".iq")

    time.sleep(10)
    
print(results)

results_file_.close()