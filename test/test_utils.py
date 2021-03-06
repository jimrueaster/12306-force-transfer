#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: JimruEaster<295140325@qq.com>

import unittest

from utils import *


class TestUtils(unittest.TestCase):
    def test_cal_interval_secs(self):
        interval_sec = calc_interval_secs('2019-05-09 12:00:00',
                                         '2019-05-09 11:00:00')
        self.assertEqual(interval_sec, 3600)
        interval_sec = calc_interval_secs('2019-05-09 11:00:00',
                                         '2019-05-09 11:00:00')
        self.assertEqual(interval_sec, 0)
        interval_sec = calc_interval_secs('2019-05-09 11:00:00',
                                         '2019-05-09 12:00:00')
        self.assertEqual(interval_sec, -3600)


if __name__ == '__main__':
    unittest.main()
