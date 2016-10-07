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

from flask import request
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource, ListResource
from xivo_confd.representations.csv_ import output_csv

from xivo_confd.plugins.switchboard.model import Switchboard

csv_header = ['date', 'entered', 'answered', 'transferred', 'abandoned', 'forwarded', 'waiting_time_average']


class SwitchboardSchema(BaseSchema):
    id = fields.String(dump_only=True)
    display_name = fields.String(dump_only=True)

    start_date = fields.DateTime(format='%Y-%m-%dT%H:%M:%S', load_only=True, missing=None)
    end_date = fields.DateTime(format='%Y-%m-%dT%H:%M:%S', load_only=True, missing=None)


class SwitchboardList(ListResource):

    model = Switchboard
    schema = SwitchboardSchema

    @required_acl('confd.switchboards.read')
    def get(self):
        return super(SwitchboardList, self).get()

    def post(self):
        return '', 405


class SwitchboardStats(ConfdResource):

    schema = SwitchboardSchema
    representations = {'text/csv; charset=utf-8': output_csv}

    def __init__(self, service):
        self.service = service

    @required_acl('confd.switchboards.{id}.stats.read')
    def get(self, id):
        form = self.schema().load(request.args.to_dict()).data
        stats = self.service.stats(id, **form)
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
