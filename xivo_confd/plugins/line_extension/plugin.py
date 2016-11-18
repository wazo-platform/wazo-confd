# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao

from xivo_confd import api
from xivo_confd.plugins.line_extension.resource import LineExtensionItem, LineExtensionList, ExtensionLineList
from xivo_confd.plugins.line_extension.legacy import LineExtensionLegacy, ExtensionLineLegacy
from xivo_confd.plugins.line_extension.service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()
        class_args = (service, line_dao, extension_dao)
        legacy_class_args = (service, line_dao, extension_dao, line_extension_dao)

        api.add_resource(LineExtensionItem,
                         '/lines/<int:line_id>/extensions/<int:extension_id>',
                         endpoint='line_extensions',
                         resource_class_args=class_args)

        api.add_resource(LineExtensionList,
                         '/lines/<int:line_id>/extensions',
                         resource_class_args=class_args)

        api.add_resource(ExtensionLineList,
                         '/extensions/<int:extension_id>/lines',
                         resource_class_args=class_args)

        api.add_resource(LineExtensionLegacy,
                         '/lines/<int:line_id>/extension',
                         endpoint='line_extension_legacy',
                         resource_class_args=legacy_class_args)

        api.add_resource(ExtensionLineLegacy,
                         '/extensions/<int:extension_id>/line',
                         resource_class_args=legacy_class_args)
