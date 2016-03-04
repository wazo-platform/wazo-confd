# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from collections import OrderedDict


def default_stat_factory():
    return {
        'abandoned': 0,
        'answered': 0,
        'entered': 0,
        'forwarded': 0,
        'transferred': 0,
        'waiting_time': [],
    }


class DailyStatAccumulator(object):

    def __init__(self):
        self.stats = OrderedDict()

    def accumulate(self, stats):
        for stat in stats:
            date = stat.time.date().strftime('%Y-%m-%d')
            self.stats.setdefault(date, default_stat_factory())
            if stat.end_type == 'abandoned':
                self.stats[date]['abandoned'] += 1
                self.stats[date]['entered'] += 1
            elif stat.end_type == 'forwarded':
                self.stats[date]['entered'] += 1
                self.stats[date]['forwarded'] += 1
            elif stat.end_type == 'transferred':
                self.stats[date]['answered'] += 1
                self.stats[date]['entered'] += 1
                self.stats[date]['transferred'] += 1
            elif stat.end_type == 'completed':
                self.stats[date]['answered'] += 1
                self.stats[date]['entered'] += 1
            self.stats[date]['waiting_time'].append(stat.wait_time)

    def results(self):
        for date, values in self.stats.iteritems():
            yield {
                'abandoned': values['abandoned'],
                'answered': values['answered'],
                'date': date,
                'entered': values['entered'],
                'forwarded': values['forwarded'],
                'transferred': values['transferred'],
                'waiting_time_average': sum(values['waiting_time']) / float(len(values['waiting_time']))
            }
