# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 Avencall
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

from xivo_dao.resources.infos import dao
from xivo_dao.resources.infos.model import Infos

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode
from xivo_confd.helpers.resource import DecoratorChain, build_response


class InfoResource(object):

    def __init__(self, dao, converter):
        self.dao = dao
        self.converter = converter

    def get(self):
        info = self.dao.get()
        response = self.converter.encode(info)
        return build_response(response)


def load(core_rest_api):
    blueprint = Blueprint('infos', __name__, url_prefix='/%s/infos' % config.API_VERSION)
    document = core_rest_api.content_parser.document(Field('uuid', Unicode()))

    converter = Converter.resource(document, Infos, 'infos', 'uuid')
    resource = InfoResource(dao, converter)

    chain = DecoratorChain(core_rest_api, blueprint)
    chain.get('').decorate(resource.get)

    core_rest_api.register(blueprint)
