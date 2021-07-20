# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.call_permission import dao as call_permission_dao

from wazo_confd.helpers.validator import (
    Optional,
    Validator,
    ValidationGroup,
)


class UniqueNameField(Validator):
    def __init__(self, dao, edit=False):
        self.dao = dao
        self.edit = edit

    def validate(self, call_permission):
        tenant_uuid = call_permission.tenant_uuid
        name = call_permission.name
        found = self.dao.find_by(tenant_uuid=tenant_uuid, name=name)
        if found is None:
            return
        elif found.id == call_permission.id:
            return

        metadata = {'tenant_uuid': tenant_uuid, 'name': name}
        raise errors.resource_exists('CallPermission', **metadata)


def build_validator():
    return ValidationGroup(
        create=[UniqueNameField(call_permission_dao)],
        edit=[Optional('name', UniqueNameField(call_permission_dao, edit=True))],
    )
