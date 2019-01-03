import os
import glob
import json
import time
import pytz
import requests
import argparse
import urllib2
import random

from dateutil import tz
from slacker import Slacker
from dateutil import parser
from datetime import datetime, timedelta
from git import Repo


argparser = argparse.ArgumentParser()
argparser.add_argument('-u', '--url', required=True,
                help="Slack URL to upload")
argparser.add_argument('-t', '--token', required=True,
                help="Slack User Token")
argparser.add_argument('-c', '--channel', required=True,
                help="Main garbage channel name")
argparser.add_argument('-i', '--important-channel', required=True,
                help="Notification and important messages channel")
args = argparser.parse_args()
slack_url = args.url
slack_token = args.token
slack_channel = args.channel
slack_important_channel = args.important_channel


def send_to_slack(msg):
    requests.post(slack_url, json={'text': msg})
def send_to_slack_important(text):
    s = Slacker(slack_token)
    channel_id = s.channels.get_channel_id(slack_important_channel)
    print text
    s.chat.command(channel=channel_id, command='/imgflip', text='sad frog; ' + text)

def imgflip(text):
    s = Slacker(slack_token)
    channel_id = s.channels.get_channel_id(slack_channel)
    s.chat.command(channel=channel_id, command='/imgflip', text=' ' + text)


def sleep(timeout):
    if isinstance(timeout, (int, long, float)):
        sleep(timedelta(seconds=timeout))

    if isinstance(timeout, timedelta):
        if timeout > timedelta(0):
            print 'Sleeping for', timeout, '\n'
            time.sleep(timeout.total_seconds())


repos_path = os.path.join(os.path.dirname(__file__), '..', '..')
gscontrol = os.path.join(repos_path, 'GSControl')
mission_repo_path = os.path.join(repos_path, 'mission')

repo = Repo(mission_repo_path)
origin = repo.remote('origin')

gs_name = ''
on_primary_gs = False
auto_session = False
auto_session_str = ''

def mark_main_session(session):
    global gs_name
    global on_primary_gs
    global auto_session
    global auto_session_str

    gs_name = os.environ['GS_NAME']
    on_primary_gs = False
    if gs_name.find(session.primary_gs) != -1:
        on_primary_gs = True
        gs_name += '-primary'

    auto_session = session.auto

    auto_session_str = ''
    if auto_session:
        auto_session_str = 'auto'


class Session:
    def __init__(self, nr, start, stop, primary_gs, auto):
        self.nr = nr
        self.start = start
        self.stop = stop
        self.primary_gs = primary_gs
        self.auto = auto

    def __repr__(self):
        return str(self.nr) + ': ' + str(self.start) + ' -> ' + \
            str(self.stop)

    def __eq__(self, other):
        if other is None:
            return False
        return self.nr == other.nr and \
               str(self.start) == str(other.start) and \
               str(self.stop) == str(other.stop) and \
               self.primary_gs == other.primary_gs and \
               self.auto == other.auto

    def __ne__(self, other):
        return not self.__eq__(other)


def parse_sessions():
    sessions = []
    for i in glob.glob(mission_repo_path + '/sessions/[1-9]*'):
        if not os.path.exists(i + '/data.json'):
            continue

        nr = i.split('/')[-1]

        j = json.load(open(i + '/data.json'))

        start = parser.parse(j['Session']['start_time_iso_with_zone']).astimezone(pytz.utc).replace(tzinfo=None)
        stop = parser.parse(j['Session']['stop_time_iso_with_zone']).astimezone(pytz.utc).replace(tzinfo=None)
        primary = j['Session'].get('primary') or ''
        auto = False
        if j['Session'].get('status') == 'auto':
            auto = True

        sessions.append(Session(nr, start, stop, primary, auto))

    return sorted(sessions, key=lambda x: x.start)


def filter_old(sessions):
    for i in sessions:
        if i.stop + timedelta(minutes=5) > datetime.utcnow():
            yield i


def execute(time_events):
    for i in time_events:
        delay = i[0] - datetime.utcnow()
        print "Waiting to run", i[1].__name__
        sleep(delay)

        print "Starting", i[1].__name__

        i[1]()

        print i[1].__name__, "finished"
        print ""

# --------------------------------------------------


session = None

while True:
    origin.pull()
    sessions = parse_sessions()
    sessions = filter(lambda i: i.stop > datetime.utcnow(), sessions)

    if len(sessions) == 0:
        print "No session found! Waiting..."
        sleep(timedelta(minutes=1))
        continue

    if session != list(sessions)[0]:
        session = list(sessions)[0]
        print "New session!"
        mark_main_session(session)

        # convert to localtime
        convert_to_local = lambda x: x.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).replace(tzinfo=None)
        local_start = convert_to_local(session.start)
        local_stop = convert_to_local(session.stop)
        send_to_slack("Next session {} scheduled at {} -> {}: {}, {}"
                      .format(session.nr, local_start, local_stop,
                              session.primary_gs, auto_session_str))

    time_left_to_session = session.start - datetime.utcnow()
    print "Session: ", session, "; Time left: ", time_left_to_session

    if time_left_to_session < timedelta(minutes=3):
        break

    # plenty of time left, fetch again
    sleep(timedelta(minutes=1))

# --------------------------------------------------


def run_cmd(cmd, name):
    print "Run: ", cmd
    if os.system(cmd) > 0:
        print " !!!" + gs_name + '/' + name + "failed!"
        send_to_slack_important(gs_name + '/' + name + "; napraw mnie")
        exit(1)


def start_session():
    j = json.load(urllib2.urlopen(urllib2.Request('https://api.imgflip.com/get_memes', headers={'User-Agent': "Magic Browser"})))
    names = [str(i['name']) for i in j['data']['memes']]
    name = random.choice(names)

    imgflip(name + '; Sesja ' + str(session.nr) + '; {} {}'.format(gs_name, auto_session_str))
    run_cmd(gscontrol + '/scripts/start_auto_session.sh ' + str(session.nr),
            'start ' + str(session.nr))


def run_keep_alive():
    if on_primary_gs and auto_session:
        run_cmd("python2 " + gscontrol + "/auto_session/execute_session.py" +
                " --downlink fp,elka --uplink " + session.primary_gs +
                " --config /gs/config.py &", 'execute_session')


def stop_keep_alive():
    if on_primary_gs and auto_session:
        run_cmd('pgrep -fx ".*/GSControl/auto_session/execute_session.py.*" | xargs kill', 'kill execute')


def stop_session():
    send_to_slack(gs_name + ': stopping session!')
    run_cmd('yes \'n\' | ' + gscontrol + '/scripts/stop_session.sh',
            'stop')
    origin.push()


def all_frames_summary():
    if on_primary_gs:
        run_cmd('yes \'y\' | ' + gscontrol + '/scripts/download_all_frames.sh ' + str(session.nr),
                'all.frames')

        run_cmd('yes \'y\' | ' + gscontrol + '/scripts/summary.sh ' + str(session.nr),
                'summary')

        with open('/tmp/stats') as stats:
            send_to_slack(stats.read())


time_events = [
    (session.start - timedelta(minutes=2), start_session),
    (session.start - timedelta(minutes=1), run_keep_alive),
    (session.stop + timedelta(seconds=30), stop_keep_alive),
    (session.stop + timedelta(minutes=1),  stop_session),
    (session.stop + timedelta(minutes=2),  all_frames_summary),
]

execute(time_events)
