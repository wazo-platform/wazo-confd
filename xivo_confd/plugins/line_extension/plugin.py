# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2015 Avencall
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

from xivo_confd.plugins.line_extension.resource import LineExtensionItem, \
    LineExtensionList, LineExtensionLegacy, ExtensionLineLegacy
from xivo_confd.plugins.line_extension.proxy import build_service


class Plugin(object):

    def load(self, core):
        api = core.api
        service = build_service()

        api.add_resource(LineExtensionItem,
                         '/lines/<int:line_id>/extensions/<int:extension_id>',
                         endpoint='line_extensions',
                         resource_class_args=(service,)
                         )

        api.add_resource(LineExtensionList,
                         '/lines/<int:line_id>/extensions',
                         resource_class_args=(service,)
                         )

        api.add_resource(LineExtensionLegacy,
                         '/lines/<int:line_id>/extension',
                         endpoint='line_extension_legacy',
                         resource_class_args=(service,)
                         )

        api.add_resource(ExtensionLineLegacy,
                         '/extensions/<int:extension_id>/line',
                         resource_class_args=(service,)
                         )
