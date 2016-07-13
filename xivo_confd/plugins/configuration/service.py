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

from xivo_dao.resources.configuration import dao as configuration_dao

from xivo_confd.plugins.configuration.notifier import build_notifier


class LiveReloadService(object):

    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def get(self):
        return {'enabled': self.dao.is_live_reload_enabled()}

    def edit(self, live_reload):
        self.dao.set_live_reload_status(live_reload)
        self.notifier.edited(live_reload)


def build_service():
    return LiveReloadService(configuration_dao,
                             build_notifier())
