# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.ingress_http import dao

from wazo_confd.helpers.validator import ValidationGroup, Validator


class CreateIngressHTTPSingleInstanceByTenantValidator(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, ingress_http):
        existing = self.dao.find_by(tenant_uuid=ingress_http.tenant_uuid)

        if existing:
            raise errors.resource_exists(
                'IngressHTTP',
                tenant_uuid=str(ingress_http.tenant_uuid),
            )


def build_validator():
    return ValidationGroup(
        create=[CreateIngressHTTPSingleInstanceByTenantValidator(dao)],
    )
