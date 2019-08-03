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


def raw_schedule(d_train_info):
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


def __train_take_hours(l_train):
    """
    火车花费小时
    :param l_train: 某一班次火车的信息
    :return: number
    """
    return int(l_train[10].split(':')[0])


def __train_take_minutes(l_train):
    """
    火车花费分钟
    :param l_train: 某一班次火车的信息
    :return: number
    """
    return int(l_train[10].split(':')[1])


def __is_specified_station(l_train, d_train_info):
    """
    skip if start station or end station doesn't match
    :param l_train: 某一班次火车的信息
    :param d_train_info: 火车信息
    :return:
    """
    return l_train[6] != d_train_info['from_station'] or l_train[7] != d_train_info['to_station']


def train_schedule(d_train_info):
    """
    获取火车时刻表
    :param d_train_info: 火车信息
    :return: list
    """
    result = []
    for train in raw_schedule(d_train_info):
        l_train = train.split('|')
        # todo 实现独立的筛选规则,作为依赖注入,以便定制"跳过不想要的班次"
        if 'G' != l_train[3][0] and 'C' != l_train[3][0]:
            # skip if not High Speed Railway
            continue
        if __is_specified_station(l_train, d_train_info):
            continue
        if l_train[9] == '24:00':
            # skip error time record
            continue

        result.append({
            'number': l_train[3],
            'start_time': d_train_info['train_date'] + ' ' + l_train[8] + ':00',
            'end_time': d_train_info['train_date'] + ' ' + l_train[9] + ':00',
            'cost_time': __train_take_hours(l_train) * 60 + __train_take_minutes(l_train)
        })

    return result


def calc_interval_secs(t1, t2):
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
        '%H:%M:%S')
    end_boarding = (dt.datetime.strptime(depart_time, '%Y-%m-%d %H:%M:%S') - dt.timedelta(minutes=5)).strftime(
        '%H:%M:%S')
    return {
        'start': start_boarding,
        'end': end_boarding
    }


def transfer_schedule(fr_tsf_simple_schedule, tsf_to_simple_schedule, set_off_date, no_more_than, from_time,
                      to_time):
    """
    过滤换乘班次
    :param fr_tsf_simple_schedule:
    :param tsf_to_simple_schedule:
    :param set_off_date:
    :param no_more_than:
    :param from_time:
    :param to_time:
    :return:
    """
    result = []
    for train1 in fr_tsf_simple_schedule:
        for train2 in tsf_to_simple_schedule:
            train1_set_off_time_end = train1['end_time']
            train2_set_off_time_start = train2['start_time']
            train2_set_off_time_end = train2['end_time']
            boarding_interval = calc_boarding_interval(train2_set_off_time_start)
            _boarding_interval_start = set_off_date + ' ' + boarding_interval['start']

            if calc_interval_secs(_boarding_interval_start, train1_set_off_time_end) / 60 <= 5:
                continue
            if calc_interval_secs(train2_set_off_time_end, train1['start_time']) / 60 > no_more_than:
                continue
            if train1['start_time'] <= set_off_date + ' %02d:00:00' % from_time:
                continue
            if train2_set_off_time_end >= set_off_date + ' %02d:00:00' % to_time:
                continue

            _res = {
                'number1': train1['number'],
                'number2': train2['number'],
                'start_time1': train1['start_time'],
                'end_time1': train1['end_time'],
                'boarding_interval': '%s-%s' % (boarding_interval['start'], boarding_interval['end']),
                'start_time2': train2['start_time'],
                'end_time2': train2['end_time'],
                'cost_time': calc_interval_secs(train2_set_off_time_end, train1['start_time']) / 60
            }
            result.append(_res)

    result = sorted(result, key=lambda s: s['start_time1'])
    result = sorted(result, key=lambda s: s['cost_time'])
    return result
