# -*- coding: UTF-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator, build_validator_bulk


class ExtensionService(CRUDService):

    def __init__(self, dao, validator, validator_bulk, notifier):
        super(ExtensionService, self).__init__(dao, validator, notifier)
        self.validator_bulk = validator_bulk

    def search(self, parameters):
        parameters['is_feature'] = True
        return self.dao.search(**parameters)

    def get(self, resource_id):
        return self.dao.get_by(id=resource_id, is_feature=True)

    def edit(self, resource, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(resource)
        self.dao.edit(resource)
        self.notifier.edited(resource, updated_fields)

    def edit_all(self, resources):
        self.validator_bulk.validate_edit(resources)
        for resource in resources:
            self.dao.edit(resource)
            self.notifier.edited(resource)


def build_service():
    return ExtensionService(extension_dao,
                            build_validator(),
                            build_validator_bulk(),
                            build_notifier())
