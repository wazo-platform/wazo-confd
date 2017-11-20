# -*- coding: utf-8 -*-
# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
