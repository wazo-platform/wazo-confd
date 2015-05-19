# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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


from xivo_dao.helpers import errors

LIVE_RELOAD_PARAM = 'enabled'


def validate_live_reload_data(data):
    if data.get(LIVE_RELOAD_PARAM) is None:
        raise errors.missing(LIVE_RELOAD_PARAM)
    if len(data) > 1:
        params = data.keys()
        params.remove(LIVE_RELOAD_PARAM)
        raise errors.unknown(*params)
