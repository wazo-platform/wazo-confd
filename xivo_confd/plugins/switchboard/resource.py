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

from flask_restful import fields, marshal, reqparse
from xivo_confd.representations.csv_ import output_csv
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.helpers.restful import DateTimeLocalZone
from xivo_confd.helpers.restful import ListResource

from xivo_confd.plugins.switchboard.model import Switchboard

switchboard_fields = {
    'id': fields.String,
    'display_name': fields.String,
}

csv_header = ['date', 'entered', 'answered', 'transferred', 'abandoned', 'forwarded', 'waiting_time_average']


class SwitchboardList(ListResource):

    model = Switchboard
    fields = switchboard_fields

    def __init__(self, service):
        self.service = service

    @required_acl('confd.switchboards.read')
    def get(self):
        params = self.search_params()
        result = self.service.search(params)
        return {'total': result.total,
                'items': [marshal(item, switchboard_fields) for item in result.items]}


class SwitchboardStats(ConfdResource):

    fields = switchboard_fields

    parser = reqparse.RequestParser()
    parser.add_argument('start_date', type=DateTimeLocalZone(), location='args')
    parser.add_argument('end_date', type=DateTimeLocalZone(), location='args')

    representations = {'text/csv; charset=utf-8': output_csv}

    def __init__(self, service):
        self.service = service

    @required_acl('confd.switchboards.{id}.stats.read')
    def get(self, id):
        args = self.parser.parse_args()
        stats = self.service.stats(id, **args)
        return {
            'headers': csv_header,
            'content': self._format_fields(stats)
        }

    def _format_fields(self, stats):
        for stat in stats:
            stat_formatted = dict(stat)
            seconds = int(stat['waiting_time_average'])
            stat_formatted['waiting_time_average'] = '{min:02}:{sec:02}'.format(min=seconds // 60, sec=seconds % 60)
            yield stat_formatted
