#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: xianjinru<xianjinru@meizu.com>
# Created on 2018-10-20 17:25

from utils import *

set_off_date = '2018-12-01'


def force_transfer(set_off_date, from_station, to_station, from_time, to_time):
    gzn_szb_timetable = get_net_schedule(set_off_date, from_station, 'IOQ')
    szb_xjl_timetable = get_net_schedule(set_off_date, 'IOQ', to_station)

    gzn_szb_simple_schedule = get_key_schedule(gzn_szb_timetable, from_station, 'IOQ')
    szb_xjl_simple_schedule = get_key_schedule(szb_xjl_timetable, 'IOQ', to_station)

    result = []
    for train1 in gzn_szb_simple_schedule:
        for train2 in szb_xjl_simple_schedule:
            datetime1_start = set_off_date + ' ' + train1['start_time'] + ':00'
            datetime1_end = set_off_date + ' ' + train1['end_time'] + ':00'
            datetime2_start = set_off_date + ' ' + train2['start_time'] + ':00'
            datetime2_end = set_off_date + ' ' + train2['end_time'] + ':00'

            if cal_interval_secs(datetime2_start, datetime1_end) / 60 < 10:
                continue
            if cal_interval_secs(datetime2_end, datetime1_start) / 60 > 120:
                continue
            if datetime1_start <= set_off_date + ' %d:00:00' % from_time:
                continue
            if datetime2_end >= set_off_date + ' %d:00:00' % to_time:
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

    print('%-6s\t%-6s\t%s\t%s\t%s\t%s\t%s' % (
        '车次1', '车次2', '开车时间1', '到达时间1', '开车时间2', '到达时间2', '耗时'))
    for project in result:
        print('%-6s\t%-6s\t%s\t%s\t%s\t%s\t%s' % (
            project['number1'], project['number2'], project['start_time1'], project['end_time1'],
            project['start_time2'],
            project['end_time2'], project['cost_time']))


force_transfer(set_off_date, 'IZQ', 'XJA', 10, 12)


force_transfer(set_off_date, 'XJA', 'IZQ', 20, 22)
