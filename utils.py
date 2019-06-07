#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: Jimru Easter<295140325@qq.com>
# Created on 2018-10-20 17:19

import datetime as dt
import json
import time

import requests


def validate_date(date_str):
    """
    验证日期
    :param date_str: 日期字符串
    :return: void
    """
    try:
        dt.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-mm-d")


def compare_date(date1, date2):
    """
    比较两个日期
    :param date1: 日期1
    :param date2: 日期2
    :return: int
    """
    validate_date(date1)
    validate_date(date2)

    t1 = time.strptime(date1, "%Y-%m-%d")
    t2 = time.strptime(date2, "%Y-%m-%d")

    if t1 < t2:
        return -1
    if t1 == t2:
        return 0
    if t1 > t2:
        return 1


def validate_set_off_date(set_off_date):
    """
    验证出发日期
    :param set_off_date: 出发日期(YYYY-mm-dd)
    :return: void
    """
    today = dt.date.today().strftime('%Y-%m-%d')
    res = compare_date(set_off_date, today)

    if res <= 0:
        raise ValueError('Date should be later than today.')


def get_raw_schedule(date, start_station, end_station):
    """
    Get Schedule from the Internet
    :param date: the date to set off
    :param start_station: the set off station
    :param end_station: the arrival station
    :return: list
    """

    payload = {'leftTicketDTO.train_date': date,
               'leftTicketDTO.from_station': start_station,
               'leftTicketDTO.to_station': end_station,
               'purpose_codes': 'ADULT'}
    url = 'https://kyfw.12306.cn/otn/leftTicket/query'
    r = requests.get(url, params=payload)
    r.encoding = 'utf-8'
    _obj = json.loads(r.text)

    return _obj['data']['result']


def get_train_schedule(date, start_station, end_station):
    """
    获取火车时刻表
    :param date: the date to set off
    :param start_station: Departure station, see the "Station List"
    :param end_station: Arrival station, see the "Station List"
    :return: dict
    """
    raw_schedule = get_raw_schedule(date, start_station, end_station)

    schedule = []
    for _train in raw_schedule:
        ft = _train.split('|')
        # todo 实现独立的筛选规则,作为依赖注入,以便定制"跳过不想要的班次"
        if 'G' != ft[3][0] and 'C' != ft[3][0]:
            # skip if not High Speed Railway
            continue
        if ft[6] != start_station or ft[7] != end_station:
            # skip if start station or end station doesn't match
            continue
        if ft[9] == '24:00':
            # skip error time record
            continue

        _cost_hour, _cost_min = map(int, ft[10].split(':'))

        _key_data = {
            'number': ft[3],
            'start_time': ft[8],
            'end_time': ft[9],
            'cost_time': _cost_hour * 60 + _cost_min
        }
        schedule.append(_key_data)
    return schedule


def cal_interval_secs(t1, t2):
    """
    (time1 - time2) and returns sec
    :param t1: time1
    :param t2: time2
    :return: int
    """
    time_tuple1 = dt.datetime.strptime(t1, '%Y-%m-%d %H:%M:%S')
    time_tuple2 = dt.datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
    interval = time_tuple1 - time_tuple2
    sec = interval.days * 24 * 3600 + interval.seconds
    return sec


def calc_boarding_interval(depart_time):
    """
    计算乘车间隔
    :param depart_time: 出发时间
    :return: dict
    """
    start_boarding = (dt.datetime.strptime(depart_time, '%Y-%m-%d %H:%M:%S') - dt.timedelta(minutes=15)).strftime(
        '%H:%M')
    end_boarding = (dt.datetime.strptime(depart_time, '%Y-%m-%d %H:%M:%S') - dt.timedelta(minutes=5)).strftime('%H:%M')
    return {
        'start': start_boarding,
        'end': end_boarding
    }
