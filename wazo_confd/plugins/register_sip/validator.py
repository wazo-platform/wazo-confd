# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from xivo_dao.resources.pjsip_transport import dao as transport_dao
from wazo_confd.helpers.validator import ValidationGroup, Validator
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

REGISTER_REGEX = re.compile(
    r'''^
                            (?:(?P<transport>.*)://)?
                            (?P<sip_username>[^:/]*)
                            (?::(?P<auth_password>[^:/]*))?
                            (?::(?P<auth_username>[^:/]*))?
                            @
                            (?P<remote_host>[^:~/]*)
                            (?::(?P<remote_port>\d*))?
                            (?:/(?P<callback_extension>[^~]*))?
                            (?:~(?P<expiration>\d*))?
                            $''',
    re.VERBOSE,
)


class GetTransportValidator(Validator):
    def validate(self, model):
        self._validate(model)

    def validate_with_tenant_uuids(self, model, tenant_uuids):
        self._validate(model, tenant_uuids)

    def _validate(self, model, tenant_uuids=None):
        register = REGISTER_REGEX.match(model.var_val)
        result = register.groupdict()
        transport_name = result['transport']
        if not transport_name:
            return

        try:
            if tenant_uuids is None:
                transport_dao.get_by(name=transport_name)
            else:
                transport_dao.get_by(name=transport_name, tenant_uuids=tenant_uuids)
        except NotFoundError:
            metadata = {'transport': transport_name}
            raise errors.param_not_found('transport', 'Transport', **metadata)


def build_validator():
    return ValidationGroup(
        create=[GetTransportValidator()], edit=[GetTransportValidator()],
    )
