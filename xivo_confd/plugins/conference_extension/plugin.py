# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.resources.conference import dao as conference_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd import api
from .resource import ConferenceExtensionItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(ConferenceExtensionItem,
                         '/conferences/<int:conference_id>/extensions/<int:extension_id>',
                         endpoint='conference_extensions',
                         resource_class_args=(service, conference_dao, extension_dao))
