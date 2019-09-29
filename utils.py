#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: Jimru Easter<295140325@qq.com>
# Created on 2018-10-20 17:19

import datetime as dt
import json

import requests

import JRUtils.simple_time as jst


def validate_set_off_date(s_set_off_date):
    """
    验证出发日期
    :param s_set_off_date: 出发日期(YYYY-mm-dd)
    :return: void
    """

    fmt = '%Y-%m-%d'
    today = dt.date.today().strftime(fmt)
    res = jst.compare_datetime(s_set_off_date, fmt, today, fmt)

    if res <= 0:
        raise ValueError('Date should be later than today.')


def schedule_cookie():
    """
    班次 Cookie
    :return: string
    """
    s = requests.session()
    s.get(url='https://kyfw.12306.cn/otn/leftTicket/init')
    cookie_jar = requests.utils.dict_from_cookiejar(s.cookies)
    result = ''
    for k, v in cookie_jar.items():
        result += '{}={}; '.format(k, v)
    return result


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
                             'purpose_codes': 'ADULT'},
                     headers={'Cookie': schedule_cookie()})
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


def __is_high_speed_railway(l_train):
    """
    是否高铁班次
    :param l_train: 某一班次火车的信息
    :return: bool
    """
    return 'G' == l_train[3][0] or 'C' == l_train[3][0]


def __is_specified_station(l_train, d_train_info):
    """
    是否指定的出发和到达站
    :param l_train: 某一班次火车的信息
    :param d_train_info: 火车信息
    :return:
    """
    return l_train[6] == d_train_info['from_station'] and l_train[7] == d_train_info['to_station']


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
        if not __is_high_speed_railway(l_train):
            continue
        if not __is_specified_station(l_train, d_train_info):
            continue
        if l_train[9] == '24:00':
            # skip error time record
            continue

        result.append({
            'number': l_train[3],
            'start_time': d_train_info['train_date'] + ' ' + l_train[8] + ':00',
            'end_time': d_train_info['train_date'] + ' ' + l_train[9] + ':00',
            'cost_time': __train_take_hours(l_train) * 60 + __train_take_minutes(l_train),
            'is_depart_from_first_station': l_train[4] == l_train[6],
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
        '%Y-%m-%d %H:%M:%S')
    end_boarding = (dt.datetime.strptime(depart_time, '%Y-%m-%d %H:%M:%S') - dt.timedelta(minutes=5)).strftime(
        '%Y-%m-%d %H:%M:%S')
    return {
        'start_time': start_boarding,
        'end_time': end_boarding
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
    :return: list
    """
    result = []
    for train1 in fr_tsf_simple_schedule:
        for train2 in tsf_to_simple_schedule:
            boarding_interval = calc_boarding_interval(train2['start_time'])

            if calc_interval_secs(boarding_interval['start_time'], train1['end_time']) / 60 <= 5:
                continue
            if calc_interval_secs(train2['end_time'], train1['start_time']) / 60 > no_more_than:
                continue
            if train1['start_time'] <= set_off_date + ' %02d:00:00' % from_time:
                continue
            if train2['end_time'] >= set_off_date + ' %02d:00:00' % to_time:
                continue

            result.append({
                'number1': train1['number'],
                'is_depart_from_first_station1': train1['is_depart_from_first_station'],
                'number2': train2['number'],
                'is_depart_from_first_station2': train2['is_depart_from_first_station'],
                'start_time1': simplify_datetime_format(train1['start_time']),
                'end_time1': simplify_datetime_format(train1['end_time']),
                'boarding_interval': '%s - %s' % (simplify_datetime_format(boarding_interval['start_time']),
                                                  simplify_datetime_format(boarding_interval['end_time'])),
                'start_time2': simplify_datetime_format(train2['start_time']),
                'end_time2': simplify_datetime_format(train2['end_time']),
                'cost_time': calc_interval_secs(train2['end_time'], train1['start_time']) / 60
            })

    result = sorted(result, key=lambda s: s['start_time1'])
    result = sorted(result, key=lambda s: s['cost_time'])
    return result


def simplify_datetime_format(s_datetime):
    """
    简化输出的时间格式
    :param s_datetime: 时间字符串
    :return: string
    """
    return jst.convert_format(s_datetime, '%Y-%m-%d %H:%M:%S', '%H:%M')


def __raw_stations():
    """
    从网络获取车站清单
    :return: string
    """
    r = requests.get(url='https://kyfw.12306.cn/otn/resources/js/framework/station_name.js')
    r.encoding = 'utf-8'
    return r.text


def station_list():
    """
    过滤获得车站列表
    :return: dict
    """
    result = {}
    for station in __raw_stations().lstrip("var station_names ='@").rstrip("';").split('@'):
        station_name = station.split('|')[1]
        station_code = station.split('|')[2]
        result[station_name] = station_code

    return result


def station_name_2_code(s_station_name):
    """
    车站名转换为代码
    :param s_station_name: 车站名
    :return: string
    """
    return station_list()[s_station_name]
