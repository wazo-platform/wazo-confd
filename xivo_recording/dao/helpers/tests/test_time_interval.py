'''
Created on Jan 23, 2013

@author: jean
'''
from xivo_recording.dao.helpers.time_interval import TimeInterval
from datetime import datetime
import unittest


class Test(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(Exception):
            TimeInterval('', '')
        with self.assertRaises(Exception):
            TimeInterval(datetime.strptime("2012-12-31", "%Y-%m-%d"),
                         datetime.strptime("2012-01-01", "%Y-%m-%d"))

    def test_intersect(self):
        interval1 = TimeInterval(datetime.strptime("2012-01-01", "%Y-%m-%d"),
                                 datetime.strptime("2012-03-01", "%Y-%m-%d"))
        interval2 = TimeInterval(datetime.strptime("2012-02-01", "%Y-%m-%d"),
                                 datetime.strptime("2012-03-31", "%Y-%m-%d"))
        result = interval2.intersect(interval1)
        self.assertTrue(result._start_date == datetime.strptime("2012-02-01",
                                                                "%Y-%m-%d"))
        self.assertTrue(result._end_date == datetime.strptime("2012-03-01",
                                                              "%Y-%m-%d"))

        interval1 = TimeInterval(datetime.strptime("2012-01-01", "%Y-%m-%d"),
                                 datetime.strptime("2012-02-01", "%Y-%m-%d"))
        interval2 = TimeInterval(datetime.strptime("2012-03-01", "%Y-%m-%d"),
                                 datetime.strptime("2012-03-31", "%Y-%m-%d"))
        result = interval2.intersect(interval1)
        self.assertTrue(result == None)
