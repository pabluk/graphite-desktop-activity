#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import json
import datetime


if len(sys.argv) < 2:
    print('Usage: report.py <activity_log>')
    sys.exit(1)

LOG_PATH = sys.argv[1]


def get_time(line):
    """
    Return a datetime object from a string

    >>> get_time('[2013-11-22 11:49:45,348] DEBUG:Key pressed')
    datetime.datetime(2013, 11, 22, 11, 49, 45)
    """
    time_mark = re.search('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
    if time_mark:
        date_str = time_mark.group(1)
        date_format = '%Y-%m-%d %H:%M:%S'
        return datetime.datetime.strptime(date_str, date_format)


def collect_data(lines):
    """
    Return a list of datetime objects from a list of lines.
    >>> lines = [
    ... '[2013-11-22 11:49:44,824] DEBUG:Key pressed',
    ... '[2013-11-22 11:49:45,024] DEBUG:Key pressed',
    ... ]
    >>> collect_data(lines)
    [datetime.datetime(2013, 11, 22, 11, 49, 44), datetime.datetime(2013, 11, 22, 11, 49, 45)]

    """
    data = []
    for line in lines:
        time = get_time(line)
        data.append(time)
    return data


def stats_by_hour(data):
    """
    Print the ocurrence number by hour.

    >>> data = [
    ... datetime.datetime(2012, 10, 16, 16, 34, 8),
    ... datetime.datetime(2012, 10, 16, 16, 47, 2),
    ... datetime.datetime(2012, 10, 16, 17, 14, 3),
    ... ]
    >>> stats_by_hour(data)
    Date: 10/16/12
    16: ## 2
    17: # 1
    """
    hour = None
    count = 0
    for time in data:
        if hour is None:
            sys.stdout.write('Date: %s\n' % time.strftime('%x'))
        if hour != time.hour:
            if not hour is None:
                sys.stdout.write(' %d\n' % count)
                count = 0
            hour = time.hour
            sys.stdout.write('%.2d: #' % hour)
            count += 1
        else:
            count += 1
            sys.stdout.write('#')
    sys.stdout.write(' %d\n' % count)


def stats_by_hour2(data):
    """
    Print the ocurrence number by hour.

    >>> data = [
    ... datetime.datetime(2012, 10, 16, 16, 34, 8),
    ... datetime.datetime(2012, 10, 16, 16, 47, 2),
    ... datetime.datetime(2012, 10, 16, 17, 14, 3),
    ... ]
    >>> stats_by_hour2(data)
    {16: 2, 17: 1}
    """
    hour = None
    count = 0
    stats = {}
    for time in data:
        if hour != time.hour:
            if not hour is None:
                #sys.stdout.write('%d],\n' % count)
                count = 0
            hour = time.hour
            #sys.stdout.write("['%.2d', " % hour)
            count += 1
            stats[hour] = count
        else:
            count += 1
            stats[hour] = count
    #sys.stdout.write('%d],\n' % count)
    return stats


def main():
    patterns = ['Key', 'button']
    lines = {}

    for p in patterns:
        lines[p] = []

    with open(LOG_PATH) as log_file:
        for line in log_file.readlines():
            for p in patterns:
                if p in line:
                    lines[p].append(line.strip())

    stats = {}
    for p in patterns:
        data = collect_data(lines[p])
        stats[p] = stats_by_hour2(data)

    hours = []
    for p in patterns:
        hours = list(set(stats[p].keys()))
    for h in hours:
        print "['%d'," % h,
        for p in patterns:
            if h in stats[p]:
                print "%d," % stats[p][h],
            else:
                print "0,",
        print "],"

    raw_data = {'p': None}
    raw_data['cols'] = [
        {'id': '', 'label': 'Hour', 'pattern':'', 'type': 'string'},
        {'id': '', 'label': 'Keyboard', 'pattern':'', 'type': 'number'},
        {'id': '', 'label': 'Mouse', 'pattern':'', 'type': 'number'},
    ]
    hours = []
    for p in patterns:
        hours = list(set(stats[p].keys()))
    raw_data['rows'] = []
    for h in hours:
        row = {'c': []}

        row['c'].append({'v': '%d' % h, 'f': None})
        for p in patterns:
            value = 0
            if h in stats[p]:
                value = stats[p][h]
            row['c'].append({'v': value, 'f': None})
        raw_data['rows'].append(row)
    json_data = json.dumps(raw_data)    
    with open('web/data.json', 'w') as f:
        f.write("var jsonData = %s;" % json_data)

if __name__ == '__main__':
    main()
