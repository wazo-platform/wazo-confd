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
from xivo_dao.resources.line.model import Line
from xivo_dao.resources.utils.search import SearchResult

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode
from xivo_confd.resources.lines import actions_sip
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain


class LineServiceProxy(object):

    def __init__(self, service):
        self.service = service

    def search(self, args):
        if 'q' in args:
            lines = self.service.find_all_by_name(args['q'])
        else:
            lines = self.service.find_all()
        return SearchResult(items=lines, total=len(lines))

    def get(self, line_id):
        return self.service.get(line_id)


def load(core_rest_api):
    blueprint = Blueprint('lines', __name__, url_prefix='/%s/lines' % config.API_VERSION)

    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('context', Unicode()),
        Field('name', Unicode()),
        Field('protocol', Unicode()),
        Field('provisioning_extension', Unicode()),
        Field('device_slot', Int()),
        Field('device_id', Unicode()),
    )
    converter = Converter.resource(document, Line)

    actions_sip.load(core_rest_api)

    service = LineServiceProxy(line_services)
    resource = CRUDResource(service, converter)

    chain = DecoratorChain(core_rest_api, blueprint)
    chain.search().decorate(resource.search)
    chain.get().decorate(resource.get)

    core_rest_api.register(blueprint)
