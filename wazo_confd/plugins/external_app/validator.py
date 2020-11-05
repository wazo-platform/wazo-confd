# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.external_app import dao as external_app_dao

from wazo_confd.helpers.validator import ValidationGroup, Validator


class UniqueNameField(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, external_app):
        tenant_uuid = external_app.tenant_uuid
        name = external_app.name
        found = self.dao.find_by(tenant_uuid=tenant_uuid, name=name)
        if found is not None:
            metadata = {'tenant_uuid': tenant_uuid, 'name': name}
            raise errors.resource_exists('ExternalApp', **metadata)


def build_validator():
    return ValidationGroup(
        create=[UniqueNameField(external_app_dao)],
    )
