# -*- coding: utf-8 -*-

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta

MONTHS = ['Sty', 'Lut', 'Mar', 'Kwi', 'Maj', 'Cze', 'Lip', 'Sie', 'Wrz', 'Paź', 'Lis', 'Gru']

OPERATORS_DEF = [
   (u'Łukasz', 'zaq32'), 
   ('Novakov', 'novakov'), 
   ('Tomek', 'tomasz.mart'),
   ('Kfazi', 'kfazi'),
   ('Mandro', 'mandro'),
   ('Piter', 'pkuligowski'),
   (u'Gumiś', 'michalgumiela'),
   ('Grzesiek', 'ggajoch'),
]

OPERATORS = sorted(map(lambda o: o[0], OPERATORS_DEF))
SLACK_NAMES = dict(map(lambda o: (o[0], o[1]), OPERATORS_DEF))

class RosterDay(object):
    def __init__(self, date, morning, evening):
        self.date = date
        self.morning = morning
        self.evening = evening
        self.operators = [self.morning, self.evening]

    def for_time(self, dt):
        if dt.hour >= 16:
            return self.evening
        else:
            return self.morning

    def __repr__(self):
        return '{:%Y-%m-%d} {}/{}'.format(self.date, self.morning, self.evening)

class Roster(object):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    def __init__(self, spreadsheet_id, credentials_file):
        self.creds = self._load_credentials(credentials_file)
        self.spreadsheet_id = spreadsheet_id
        
        service = build('sheets', 'v4', credentials=self.creds)
        self.api = service.spreadsheets()

    def find_assignment_for_date(self, date):
        assignments = self._download_month(date)

        result = filter(lambda a: a.date.date() == date.date(), assignments)
        if result:
            return result[0]
        else:
            return None

    def _group_week(self, days, mornings, evenings):
        result = []

        for i in range(0, 7):
            day = days[i] or '' if i < len(days) else ''
            morning = mornings[i] or '' if i < len(mornings) else ''
            evening = evenings[i] or '' if i < len(evenings) else ''

            if day == '':
                continue

            day = int(day.strip())

            result.append((day, morning, evening))

        return result

    def _download_month(self, month_start):
        month_start = datetime(year=month_start.year, month=month_start.month, day=1)
        result = self.api.values().get(
            spreadsheetId=self.spreadsheet_id, 
            range='{} {:%y}!B4:H18'.format(MONTHS[month_start.month - 1], month_start)
        ).execute()
        values = result.get('values', [])

        weeks = [
            self._group_week(
                values[i], 
                values[i + 1] if i + 1 < len(values) else [], 
                values[i + 2] if i + 1 < len(values) else []
            )
            for i in range(0, len(values), 3)
        ]

        assignments = []
        
        for week in weeks:
            for (day, m, e) in week:
                a = RosterDay(month_start + timedelta(days=day - 1), m, e)
                assignments.append(a)

        return assignments

    def _load_credentials(self, credentials_file):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('google-token.pickle'):
            with open('google-token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, Roster.SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('google-token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds
