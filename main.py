#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: xianjinru<xianjinru@meizu.com>
# Created on 2018-10-20 17:25

import time

from pandas import DataFrame
from tabulate import tabulate

from utils import *

date = '2019-01-16'


def force_transfer(set_off_date, from_station, transfer_station, to_station, from_time, to_time, no_more_than,
                   print_res=True):
    '''
    main function
    :param string set_off_date: 'yyyy-mm-dd'
    :param string from_station: 12306 code
    :param string transfer_station: 12306 code
    :param string to_station: 12306 code
    :param int from_time: hh
    :param int to_time: hh
    :param int no_more_than: mins
    :param bool print_res:
    :return:
    '''

    try:
        _set_off = time.mktime(datetime.strptime(set_off_date, "%Y-%m-%d").timetuple())
        _now = time.time()

        if _set_off < _now:
            raise Exception('Date error')
    except Exception as e:
        print('Exception occurred, value:', e)
        return

    fr_tsf_timetable = get_net_schedule(set_off_date, from_station, transfer_station)
    tsf_to_timetable = get_net_schedule(set_off_date, transfer_station, to_station)

    fr_tsf_simple_schedule = get_key_schedule(fr_tsf_timetable, from_station, transfer_station)
    tsf_to_simple_schedule = get_key_schedule(tsf_to_timetable, transfer_station, to_station)

    result = []
    for train1 in fr_tsf_simple_schedule:
        for train2 in tsf_to_simple_schedule:
            datetime1_start = set_off_date + ' ' + train1['start_time'] + ':00'
            datetime1_end = set_off_date + ' ' + train1['end_time'] + ':00'
            datetime2_start = set_off_date + ' ' + train2['start_time'] + ':00'
            datetime2_end = set_off_date + ' ' + train2['end_time'] + ':00'

            if cal_interval_secs(datetime2_start, datetime1_end) / 60 < 10:
                continue
            if cal_interval_secs(datetime2_end, datetime1_start) / 60 > no_more_than:
                # if this set off time make the trip longer than the limit time,
                # then this loop can directly break 
                # because the time will longer than current result
                break
            if datetime1_start <= set_off_date + ' %02d:00:00' % from_time:
                continue
            if datetime2_end >= set_off_date + ' %02d:00:00' % to_time:
                continue
            _res = {
                'number1': train1['number'],
                'number2': train2['number'],
                'start_time1': train1['start_time'],
                'end_time1': train1['end_time'],
                'start_time2': train2['start_time'],
                'end_time2': train2['end_time'],
                'cost_time': cal_interval_secs(datetime2_end, datetime1_start) / 60
            }
            result.append(_res)

    result = sorted(result, key=lambda s: s['start_time1'])
    result = sorted(result, key=lambda s: s['cost_time'])

    if not print_res:
        return result
    result_list = [x.values() for x in result]

    df = DataFrame(result_list)

    headers = ['Train1', 'Train2', 'Train1 Depart', 'Train1 Arrive', 'Train2 Depart',
               'Train2 Arrive', 'Cost Time(min)']
    print(tabulate(df, headers=headers, tablefmt='fancy_grid', showindex=False))
    return result


print()
print(u'广州南->香港西九龙', end='\n\n')
force_transfer(set_off_date=date, from_station='IZQ', transfer_station='IOQ',
               to_station='XJA', from_time=10, no_more_than=90, to_time=12)

print()
print(u'香港西九龙->广州南', end='\n\n')
force_transfer(set_off_date=date, from_station='XJA', transfer_station='IOQ',
               to_station='IZQ', from_time=20, no_more_than=90, to_time=22)
