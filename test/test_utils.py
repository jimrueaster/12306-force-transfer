#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: JimruEaster<295140325@qq.com>

import unittest

from utils import *


class TestUtils(unittest.TestCase):
    def test_cal_interval_secs(self):
        interval_sec = cal_interval_secs('2019-05-09 12:00:00',
                                         '2019-05-09 11:00:00')
        self.assertEqual(interval_sec, 3600)
        interval_sec = cal_interval_secs('2019-05-09 11:00:00',
                                         '2019-05-09 11:00:00')
        self.assertEqual(interval_sec, 0)
        interval_sec = cal_interval_secs('2019-05-09 11:00:00',
                                         '2019-05-09 12:00:00')
        self.assertEqual(interval_sec, -3600)

    def test_compare_date(self):
        ret = compare_date('2019-05-08', '2019-05-09')
        self.assertEqual(ret, -1)
        ret = compare_date('2019-05-09', '2019-05-09')
        self.assertEqual(ret, 0)
        ret = compare_date('2019-05-10', '2019-05-09')
        self.assertEqual(ret, 1)


if __name__ == '__main__':
    unittest.main()
