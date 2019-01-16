# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao

from .legacy import LineExtensionLegacy, ExtensionLineLegacy
from .resource import LineExtensionItem, LineExtensionList, ExtensionLineList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()
        class_args = (service, line_dao, extension_dao)
        legacy_class_args = (service, line_dao, extension_dao, line_extension_dao)

        api.add_resource(
            LineExtensionItem,
            '/lines/<int:line_id>/extensions/<int:extension_id>',
            endpoint='line_extensions',
            resource_class_args=class_args
        )

        api.add_resource(
            LineExtensionList,
            '/lines/<int:line_id>/extensions',
            resource_class_args=class_args
        )

        api.add_resource(
            ExtensionLineList,
            '/extensions/<int:extension_id>/lines',
            resource_class_args=class_args
        )

        api.add_resource(
            LineExtensionLegacy,
            '/lines/<int:line_id>/extension',
            endpoint='line_extension_legacy',
            resource_class_args=legacy_class_args
        )

        api.add_resource(
            ExtensionLineLegacy,
            '/extensions/<int:extension_id>/line',
            resource_class_args=legacy_class_args
        )
