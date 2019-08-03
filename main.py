#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: Jimru Easter<295140325@qq.com>
# Created on 2018-10-20 17:25

from datetime import datetime
from datetime import timedelta

from pandas import DataFrame
from tabulate import tabulate

from utils import *

date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')


def smart_transfer(set_off_date, from_station, transfer_station, to_station, from_time, to_time, no_more_than):
    """
    main function
    :param string set_off_date: 'yyyy-mm-dd'
    :param string from_station: 12306 code
    :param string transfer_station: 12306 code
    :param string to_station: 12306 code
    :param int from_time: hh
    :param int to_time: hh
    :param int no_more_than: mins
    :return:
    """

    validate_set_off_date(set_off_date)

    fr_tsf_simple_schedule = train_schedule({
        'train_date': set_off_date,
        'from_station': from_station,
        'to_station': transfer_station,
    })
    tsf_to_simple_schedule = train_schedule({
        'train_date': set_off_date,
        'from_station': transfer_station,
        'to_station': to_station,
    })

    result = transfer_schedule(fr_tsf_simple_schedule, tsf_to_simple_schedule, set_off_date, no_more_than,
                               from_time, to_time)

    return result


def print_schedule_as_table(schedule):
    """
    以表格形式输出班次
    :param schedule:
    :return:
    """
    result_list = [x.values() for x in schedule]

    df = DataFrame(result_list)

    headers = ['Train1', 'Train2', 'Train1 Depart', 'Train1 Arrive', 'Boarding', 'Train2 Depart',
               'Train2 Arrive', 'Cost Time(min)']
    print(tabulate(df, headers=headers, tablefmt='fancy_grid', showindex=False))


print()
print(u'广州南->香港西九龙', end='\n\n')
from_trans_schedule = smart_transfer(set_off_date=date, from_station='IZQ', transfer_station='IOQ',
                                     to_station='XJA', from_time=10, no_more_than=90, to_time=12)
print_schedule_as_table(from_trans_schedule)

print()
print(u'香港西九龙->广州南', end='\n\n')
trans_to_schedule = smart_transfer(set_off_date=date, from_station='XJA', transfer_station='IOQ',
                                   to_station='IZQ', from_time=20, no_more_than=90, to_time=22)

print_schedule_as_table(trans_to_schedule)
