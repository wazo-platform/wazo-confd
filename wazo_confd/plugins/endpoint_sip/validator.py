# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

# Do not allow to set loop in template
from functools import partial

from xivo_dao.helpers import errors
from xivo_dao.resources.endpoint_sip import dao as sip_dao_module
from xivo_dao.resources.pjsip_transport import dao as transport_dao

from wazo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    Validator,
    ValidationGroup,
)


class EndpointSIPTemplatesValidator(Validator):
    def validate(self, template):
        self.validate_not_itself(template)

    def validate_not_itself(self, template):
        if template in template.templates:
            raise errors.not_permitted('Cannot use itself as template')


def build_validator():
    sip_find_by = partial(sip_dao_module.find_by, template=False)
    template_find_by = partial(sip_dao_module.find_by, template=True)
    return ValidationGroup(
        create=[
            Optional(
                'name',
                UniqueField('name', lambda v: sip_find_by(name=v), 'SIPEndpoint'),
                UniqueField('name', lambda v: template_find_by(name=v), 'SIPEndpointTemplate'),
                UniqueField('name', lambda v: transport_dao.find_by(name=v), 'Transport'),
            ),
        ],
        edit=[
            EndpointSIPTemplatesValidator(),
            Optional(
                'name',
                UniqueFieldChanged('name', sip_find_by, 'SIPEndpoint', id_field='uuid'),
                UniqueFieldChanged('name', template_find_by, 'SIPEndpointTemplate', id_field='uuid'),
                UniqueFieldChanged('name', transport_dao.find_by, 'Transport', id_field='uuid'),
            )
        ],
    )
