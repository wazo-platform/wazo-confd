# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidationAssociation, ValidatorAssociation


class ValidateLineApplicationAssociation(ValidatorAssociation):
    def validate(self, line, application):
        self.validate_same_tenant(line, application)
        self.validate_not_already_associated(line, application)

    def validate_same_tenant(self, line, application):
        if line.tenant_uuid != application.tenant_uuid:
            raise errors.different_tenants(
                line_tenant_uuid=line.tenant_uuid,
                application_tenant_uuid=application.tenant_uuid,
            )

    def validate_not_already_associated(self, line, application):
        if line.application_uuid is not None:
            raise errors.resource_associated(
                'Line',
                'Application',
                line_id=line.id,
                application_uuid=line.application_uuid,
            )


def build_validator():
    return ValidationAssociation(association=[ValidateLineApplicationAssociation()])
