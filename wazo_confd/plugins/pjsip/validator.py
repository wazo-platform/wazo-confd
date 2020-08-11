# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import partial

from xivo_dao.helpers import errors
from xivo_dao.resources.pjsip_transport import dao as transport_dao_module
from xivo_dao.resources.endpoint_sip import dao as sip_dao_module

from wazo_confd.helpers.validator import (
    UniqueField,
    UniqueFieldChanged,
    Validator,
    ValidationGroup,
)
from wazo_confd.helpers.asterisk import PJSIPDocValidator


class TransportDeleteValidator(Validator):
    def __init__(self, sip_dao):
        self.sip_dao = sip_dao

    def validate(self, transport, fallback):
        if not fallback:
            self._validate_not_associated(transport)

    def _validate_not_associated(self, transport):
        sip = self.sip_dao.find_by(tenant_uuids=None, transport_uuid=transport.uuid)
        if sip:
            raise errors.resource_associated(
                'Transport',
                'EndpointSIP',
                transport_uuid=transport.uuid,
                endpoint_sip_uuid=sip.uuid,
            )


def build_pjsip_transport_validator(pjsip_doc):
    sip_find_by = partial(sip_dao_module.find_by, template=False)
    template_find_by = partial(sip_dao_module.find_by, template=True)
    return ValidationGroup(
        create=[
            UniqueField(
                'name', lambda name: transport_dao_module.find_by(name=name), 'name'
            ),
            UniqueField('name', lambda name: sip_find_by(name=name), 'name'),
            UniqueField('name', lambda name: template_find_by(name=name), 'name'),
            PJSIPDocValidator('options', 'transport', pjsip_doc),
        ],
        edit=[
            UniqueFieldChanged('name', transport_dao_module.find_by, 'Transport', id_field='uuid'),
            UniqueFieldChanged('name', sip_find_by, 'SIPEndpoint', id_field='uuid'),
            UniqueFieldChanged('name', template_find_by, 'SIPEndpointTemplate', id_field='uuid'),
            PJSIPDocValidator('options', 'transport', pjsip_doc),
        ],
        delete=[TransportDeleteValidator(sip_dao_module)],
    )
