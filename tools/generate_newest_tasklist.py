import os
import json
import pytz
from glob import glob
from dateutil import parser
from datetime import datetime, timedelta
from git import Repo, PushInfo

folder = os.path.dirname(os.path.abspath(__file__))

repo = Repo(folder + '/../../mission')
mission_origin = repo.remote('origin')


def get_sorted_catalogs():
    all = glob(folder + '/../../mission/sessions/*')

    all_sorted = []
    for i in all:
        if i.split('/')[-1].isdigit():
            all_sorted.append(i)

    return sorted(all_sorted, key=lambda x: int(x.split('/')[-1]))


sessions = get_sorted_catalogs()

last_non_auto = None

for i in sessions:
    session_nr = int(i.split('/')[-1])
    file = os.path.join(i, 'data.json')
    if not os.path.isfile(file):
        continue

    data = json.loads(open(file).read())['Session']
    if data['short_description'] == 'Automatic session.':
        continue
    
    date = parser.parse(data['start_time_iso_with_zone']).astimezone(pytz.utc).replace(tzinfo=None)

    if date < datetime.utcnow():
        last_non_auto = [session_nr, data]
        continue

    # `date` is next upcoming non-auto session
    start = last_non_auto[0]
    end = session_nr
    print "Generating telemetry download between session {} and {}!".format(start, end)

    template = None

    if data['short_description'].find("Power cycle EPS A.") != -1:
        print "Power cycle A!"
        template = 'power_cycle_A.template'
    elif data['short_description'].find("Power cycle EPS B.") != -1:
        print "Power cycle B!"
        template = 'power_cycle_B.template'
    elif data['short_description'].find("Telemetry download.") != -1:
        print "!!!!!!  Just telemetry download! Make sure this is correct  !!!!!!"
        template = 'telemetry_download.template'
    else:
        print "!!!!!!  Incorrect description  !!!!!!"
        exit(1)

    template = folder + '/tasklist_templates/' + template
    output = folder + '/../../mission/sessions/' + str(end) + '/tasklist.py'
    os.system("python2 " + folder + "/generate_tasklist.py -s {} -e {} -t {} -o {}".format(start, end, template, output))

    branch = 'session_' + str(end)
    repo.git.checkout('master')
    mission_origin.pull(rebase=True)
    repo.git.checkout('HEAD', b=branch)
    repo.git.add('sessions/' + str(end) + '/tasklist.py')
    repo.git.commit(m=branch)
    repo.git.push('--set-upstream', 'origin', branch)

    exit(0)
    