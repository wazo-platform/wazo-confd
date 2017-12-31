# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class ExtensionService(CRUDService):

    def search(self, parameters):
        parameters['is_feature'] = True
        return self.dao.search(**parameters)

    def get(self, resource_id):
        return self.dao.get_by(id=resource_id, is_feature=True)


def build_service():
    return ExtensionService(extension_dao,
                            build_validator(),
                            build_notifier())
