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
from xivo_dao.data_handler.cti_profile import dao
from xivo_dao.resources.cti_profile.model import CtiProfile
from xivo_dao.data_handler.utils.search import SearchResult

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain


class CtiProfileService(object):

    def __init__(self, dao):
        self.dao = dao

    def search(self, args):
        items = self.dao.find_all()
        return SearchResult(items=items, total=len(items))

    def get(self, profile_id):
        return self.dao.get(profile_id)


def load(core_rest_api):
    blueprint = Blueprint('cti_profiles', __name__, url_prefix='/%s/cti_profiles' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('name', Unicode())
    )
    converter = Converter.resource(document, CtiProfile, 'cti_profiles')

    service = CtiProfileService(dao)
    resource = CRUDResource(service, converter)

    chain = DecoratorChain(core_rest_api, blueprint)
    chain.search().decorate(resource.search)
    chain.get().decorate(resource.get)

    core_rest_api.register(blueprint)
