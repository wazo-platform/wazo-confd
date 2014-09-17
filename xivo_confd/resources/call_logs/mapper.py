# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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


def to_api(call_log):
    result = {}
    result['Call Date'] = call_log.date.isoformat()
    result['Caller'] = '%s (%s)' % (call_log.source_name, call_log.source_exten)
    result['Called'] = call_log.destination_exten
    result['Period'] = _format_duration(call_log.duration)
    result['user Field'] = call_log.user_field or ''
    return result


def _format_duration(duration):
    return str(int(round(duration.total_seconds())))
