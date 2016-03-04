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

from xivo_dao.resources.switchboard import dao as switchboard_dao

from xivo_confd.plugins.switchboard.stats import DailyStatAccumulator


class SwitchboardService(object):

    def __init__(self, dao):
        self.dao = dao

    def search(self, parameters):
        return self.dao.search(**parameters)

    def stats(self, switchboard_id):
        stats = self.dao.stats(switchboard_id)
        accumulator = DailyStatAccumulator()
        accumulator.accumulate(stats)
        return accumulator.results()


def build_service():
    switchboard_service = SwitchboardService(switchboard_dao)

    return switchboard_service
