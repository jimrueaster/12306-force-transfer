#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: xianjinru<xianjinru@meizu.com>
# Created on 2018-10-20 17:19

import json
from datetime import datetime

import requests


def get_net_schedule(date):
    '''
    Get Schedule from the Internet
    :param date: the date to set off
    :return: list
    '''
    payload = {'leftTicketDTO.train_date': date,
               'leftTicketDTO.from_station': 'IZQ',
               'leftTicketDTO.to_station': 'IOQ',
               'purpose_codes': 'ADULT'}
    url = 'https://kyfw.12306.cn/otn/leftTicket/query'
    r = requests.get(url, params=payload)
    r.encoding = 'utf-8'
    _obj = json.loads(r.text)

    return _obj['data']['result']


def get_key_schedule(origin_data, start_station, end_station):
    '''
    Get the interesting
    :param origin_data: original result from 12306 website
    :param start_station: Departure station, see the "Station List"
    :param end_station: Arrival station, see the "Station List"
    :return: dict
    '''
    schedule = []
    for _train in origin_data:
        ft = _train.split('|')
        if 'G' != ft[3][0]:
            continue
        if ft[6] != start_station or ft[7] != end_station:
            continue

        _key_data = {
            'number': ft[3],
            'start_time': ft[8],
            'end_time': ft[9],
            'cost_time': ft[10].split(':')[1]
        }
        schedule.append(_key_data)
    return schedule


def cal_interval_secs(t1, t2):
    '''
    (time1 - time2) and returns sec
    :param t1: time1
    :param t2: time2
    :return: int
    '''
    time_tuple1 = datetime.strptime(t1, '%Y-%m-%d %H:%M:%S')
    time_tuple2 = datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
    interval = time_tuple1 - time_tuple2
    sec = interval.days * 24 * 3600 + interval.seconds
    return sec
