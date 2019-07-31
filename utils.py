#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: Jimru Easter<295140325@qq.com>
# Created on 2018-10-20 17:19

import datetime as dt
import json

import requests

import JRUtils.simple_time as jst


def validate_set_off_date(set_off_date):
    """
    验证出发日期
    :param set_off_date: 出发日期(YYYY-mm-dd)
    :return: void
    """

    fmt = '%Y-%m-%d'
    today = dt.date.today().strftime(fmt)
    res = jst.compare_datetime(set_off_date, fmt, today, fmt)

    if res <= 0:
        raise ValueError('Date should be later than today.')


def get_raw_schedule(d_train_info):
    """
    Get Schedule from the Internet
    :param d_train_info: 火车信息
    :return: list
    """
    r = requests.get(url='https://kyfw.12306.cn/otn/leftTicket/query',
                     params={'leftTicketDTO.train_date': d_train_info['train_date'],
                             'leftTicketDTO.from_station': d_train_info['from_station'],
                             'leftTicketDTO.to_station': d_train_info['to_station'],
                             'purpose_codes': 'ADULT'})
    r.encoding = 'utf-8'
    result = json.loads(r.text)

    return result['data']['result']


def get_train_schedule(d_train_info):
    """
    获取火车时刻表
    :param d_train_info: 火车信息
    :return: list
    """
    raw_schedule = get_raw_schedule(
        {
            'train_date': d_train_info['train_date'],
            'from_station': d_train_info['from_station'],
            'to_station': d_train_info['to_station'],
        }
    )

    schedule = clean_raw_schedule(raw_schedule, d_train_info)
    return schedule


def clean_raw_schedule(l_raw_schedule, d_train_info):
    """
    清洗班次原始数据
    :param l_raw_schedule: 原始班次
    :param d_train_info: 火车信息
    :return: list
    """
    result = []
    for train in l_raw_schedule:
        l_train = train.split('|')
        # todo 实现独立的筛选规则,作为依赖注入,以便定制"跳过不想要的班次"
        if 'G' != l_train[3][0] and 'C' != l_train[3][0]:
            # skip if not High Speed Railway
            continue
        if l_train[6] != d_train_info['from_station'] or l_train[7] != d_train_info['to_station']:
            # skip if start station or end station doesn't match
            continue
        if l_train[9] == '24:00':
            # skip error time record
            continue

        _cost_hour, _cost_min = map(int, l_train[10].split(':'))

        result.append({
            'number': l_train[3],
            'start_time': l_train[8],
            'end_time': l_train[9],
            'cost_time': _cost_hour * 60 + _cost_min
        })

    return result


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
