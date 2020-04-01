# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.pjsip_transport import dao

from wazo_confd.helpers.validator import (
    UniqueField,
    UniqueFieldChanged,
    Validator,
    ValidationGroup,
)


class PJSIPDocValidator(Validator):
    def __init__(self, field, section, pjsip_doc):
        self.field = field
        self.pjsip_doc = pjsip_doc
        self.section = section

    def validate(self, model):
        self._validate(model)

    def _validate(self, model):
        values = getattr(model, self.field, [])
        option_names = [value[0] for value in values]
        for option_name in option_names:
            if not self.pjsip_doc.is_valid_in_section(self.section, option_name):
                raise errors.invalid_choice(
                    field='{}: invalid variable ({})'.format(self.field, option_name),
                    choices=self.pjsip_doc.get_section_variables(self.section),
                )


def build_pjsip_transport_validator(pjsip_doc):
    return ValidationGroup(
        create=[
            UniqueField('name', lambda name: dao.find_by(name=name), 'name'),
            PJSIPDocValidator('options', 'transport', pjsip_doc),
        ],
        edit=[
            UniqueFieldChanged('name', dao, 'Transport', id_field='uuid'),
            PJSIPDocValidator('options', 'transport', pjsip_doc),
        ],
    )
