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
print(date)


def print_stations(d_stations):
    print("{}->{}->{}".format(d_stations['from_station'], d_stations['transfer_station'], d_stations['to_station']),
          end='\n\n')


# todo 封装代码
stations = {
    'from_station': '广州南',
    'transfer_station': '深圳北',
    'to_station': '香港西九龙',
}

print_stations(stations)


def smart_transfer(s_set_off_date, d_stations, i_from_time, i_to_time, i_no_more_than):
    """
    main function
    :param s_set_off_date: 'yyyy-mm-dd'
    # todo fix wrong comments
    :param d_stations: {
        'train_date': set_off_date,
        'from_station': from_station,
        'to_station': transfer_station,
    }
    :param i_from_time: hh
    :param i_to_time: hh
    :param i_no_more_than: minutes
    :return:
    """
    validate_set_off_date(s_set_off_date)

    fr_tsf_simple_schedule = train_schedule({
        'train_date': s_set_off_date,
        'from_station': station_name_2_code(d_stations['from_station']),
        'to_station': station_name_2_code(d_stations['transfer_station']),
    })
    tsf_to_simple_schedule = train_schedule({
        'train_date': s_set_off_date,
        'from_station': station_name_2_code(d_stations['transfer_station']),
        'to_station': station_name_2_code(d_stations['to_station']),
    })

    result = transfer_schedule(fr_tsf_simple_schedule, tsf_to_simple_schedule, s_set_off_date, i_no_more_than,
                               i_from_time, i_to_time)

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


from_trans_schedule = smart_transfer(s_set_off_date=date, d_stations=stations, i_from_time=10, i_no_more_than=90,
                                     i_to_time=12)
print_schedule_as_table(from_trans_schedule)

print(u'\n香港西九龙->广州南', end='\n\n')


def reverse_stations(d_stations):
    """
    翻转出发/换乘/到达站
    :param d_stations:  {
        'from_station': '广州南',
        'transfer_station': '深圳北',
        'to_station': '香港西九龙',
    }
    :return:
    """
    return {
        'from_station': d_stations['to_station'],
        'transfer_station': d_stations['transfer_station'],
        'to_station': d_stations['from_station'],
    }


trans_to_schedule = smart_transfer(s_set_off_date=date, d_stations=reverse_stations(stations), i_from_time=20,
                                   i_no_more_than=90,
                                   i_to_time=22)

print_schedule_as_table(trans_to_schedule)
