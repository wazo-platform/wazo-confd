# -*- coding: UTF-8 -*-
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from datetime import datetime


class TimeInterval(object):
    '''
    Represents a time interval: start_date ==> end_date
    '''

    def __init__(self, start_date, end_date):
        '''
        Creates a TimeInterval object using two DateTime objects
        '''
        if(type(start_date) != datetime and type(end_date) != datetime):
            raise Exception('Two datetime objects must be provided.')
        if(start_date > end_date):
            raise Exception('Start date must be lesser than end date')
        self._start_date = start_date
        self._end_date = end_date

    def intersect(self, other_interval):
        '''
        Return a TimeInterval object representing the intersection between
        two time intervals, None if they do not intersect
        '''
        if(type(other_interval) != TimeInterval):
            raise Exception('A TimeInterval object must be provided.')
        if(self._start_date >= other_interval._end_date or\
           self._end_date <= other_interval._start_date):
            return None
        else:
            max_start = max(self._start_date, other_interval._start_date)
            min_end = min(self._end_date, other_interval._end_date)
            return TimeInterval(max_start, min_end)
