# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.moh import dao as moh_dao

from wazo_confd.helpers.validator import ValidationGroup, Validator


class MOHExists(Validator):
    def __init__(self, dao_get_by):
        self.dao_get_by = dao_get_by

    def validate(self, application):
        self.validate_moh_exists_in_tenant(application)

    def validate_moh_exists_in_tenant(self, application):
        if not application.dest_node:
            return
        if not application.dest_node.type_ == 'holding':
            return
        moh_name = application.dest_node.music_on_hold
        if moh_name:
            if moh_name == 'default':
                return
            try:
                self.dao_get_by(name=moh_name, tenant_uuids=[application.tenant_uuid])
            except NotFoundError:
                metadata = {'music_on_hold': moh_name}
                raise errors.param_not_found('music_on_hold', 'MOH', **metadata)


def build_validator():
    moh_validator = MOHExists(moh_dao.get_by)
    return ValidationGroup(create=[moh_validator], edit=[moh_validator])
