# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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


from flask import Blueprint
from xivo_confd.resources.line import services as line_services
from xivo_dao.resources.line.model import LineSIP
from xivo_dao.resources.utils.search import SearchResult

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain


class LineSIPServiceProxy(object):

    def __init__(self, service):
        self.service = service

    def search(self, args):
        lines = self.service.find_all_by_protocol('sip')
        return SearchResult(items=lines, total=len(lines))

    def get(self, line_id):
        return self.service.get(line_id)

    def create(self, line):
        self.fix_line(line)
        line.name = line.username
        return self.service.create(line)

    def edit(self, line):
        line.name = line.username
        return self.service.edit(line)

    def delete(self, line):
        self.service.delete(line)

    def fix_line(self, line):
        for field in line._MAPPING.values():
            if not hasattr(line, field):
                setattr(line, field, None)


def load(core_rest_api):
    blueprint = Blueprint('lines_sip', __name__, url_prefix='/%s/lines_sip' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('context', Unicode()),
        Field('username', Unicode()),
        Field('secret', Unicode()),
        Field('provisioning_extension', Unicode()),
        Field('device_slot', Int()),
        Field('callerid', Unicode()),
    )
    converter = Converter.resource(document, LineSIP, 'lines_sip')

    service = LineSIPServiceProxy(line_services)
    resource = CRUDResource(service, converter)

    DecoratorChain.register_scrud(core_rest_api, blueprint, resource)
