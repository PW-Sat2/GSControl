# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from roster import Roster, OPERATORS
from datetime import datetime
from pprint import pprint
from random import Random

roster = Roster('1RrK5RQMWtoE-6tf9BmMLXoLmMOboBQ-doXpRB51Fy7I', 'C:/PW-Sat/mission-data/google-credentials.json')

R = Random(x=42)

def select_operator(last_assignments, exclude=[]):
    s = sorted(last_assignments, key=last_assignments.get)

    for item in s:
        print('{} in {}: {}'.format(item, exclude, item in exclude))
        if item in exclude:
            continue

        return item

def find_last_assignments(assignments, operators):
    mornings = dict(map(lambda op: (op, None), operators))
    evenings = dict(map(lambda op: (op, None), operators))

    for day in reversed(assignments):
        if day.morning and day.morning in operators and not mornings[day.morning]:
            mornings[day.morning] = day.date

        if day.evening and day.evening in operators and not evenings[day.evening]:
            evenings[day.evening] = day.date

    return (mornings, evenings)


def fill_assignment(empty_assignment_idx, all_assignments):
    empty_assignment = all_assignments[empty_assignment_idx]
    
    previous = all_assignments[:empty_assignment_idx]
    day_before = all_assignments[empty_assignment_idx - 1]
    day_after = all_assignments[empty_assignment_idx + 1] if len(all_assignments) > empty_assignment_idx + 1 else None

    operator_pool = list(OPERATORS)
    
    for a in [day_before, empty_assignment, day_after]:
        if a is None:
            continue
        for op in a.operators:
            if op and op in operator_pool:
                print('Removing {}'.format(op))
                operator_pool.remove(op)

    if len(operator_pool) == 0:
        print('Everyone removed from pool!')
        operator_pool = list(OPERATORS) # just in case

    (last_morning, last_evening) = find_last_assignments(previous, operator_pool)

    both_empty = not empty_assignment.morning and not empty_assignment.evening

    if not empty_assignment.morning:
        print('Moringin: {}'.format(empty_assignment.operators))
        empty_assignment.assign_morning(select_operator(last_morning, empty_assignment.operators))

    if not empty_assignment.evening:
        print('Eve: {}'.format(empty_assignment.operators))
        empty_assignment.assign_evening(select_operator(last_evening, empty_assignment.operators))

    if both_empty and R.random() <= 0.3:
        print('Swapping {}'.format(empty_assignment.operators))
        empty_assignment.swap_operators()

    print(empty_assignment)

def main():
    assignments_per_month = [
        # roster.download_month(datetime(year=2019, month=3, day=1)),
        # roster.download_month(datetime(year=2019, month=4, day=1)),
        roster.download_month(datetime(year=2019, month=5, day=1)),
        roster.download_month(datetime(year=2019, month=6, day=1)),
        roster.download_month(datetime(year=2019, month=7, day=1)),
    ]

    assignments = []
    for month in assignments_per_month:
        assignments.extend(month)

    empty_assignments = filter(lambda x: not x.morning or not x.evening, assignments)
    pprint(empty_assignments)

    for empty in empty_assignments:
        print('Empty: {}'.format(empty.date))
        fill_assignment(assignments.index(empty), assignments)

    pprint(empty_assignments)

main()