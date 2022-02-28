# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from marshmallow import fields, post_dump
from marshmallow.validate import Length, OneOf
from marshmallow.utils import get_value

from wazo_confd.helpers.mallow import (
    BaseSchema,
    Link,
    ListLink,
    Nested,
    PJSIPSection,
    PJSIPSectionOption,
)

logger = logging.getLogger(__name__)


class OptionsField(fields.List):
    def __init__(self, **kwargs):
        kwargs.setdefault('missing', [])
        kwargs.setdefault('validate', Length(max=512))
        option_schema = PJSIPSectionOption(option_regex=None)
        super().__init__(option_schema, **kwargs)


class GETQueryStringSchema(BaseSchema):
    view = fields.String(validate=OneOf(['merged']), missing=None)


class EndpointSIPRelationSchema(BaseSchema):
    uuid = fields.UUID(required=True)
    label = fields.String(dump_only=True)


class TransportRelationSchema(BaseSchema):
    uuid = fields.UUID(required=True)


class _BaseSIPSchema(BaseSchema):
    def get_attribute(self, obj, attr, default):
        only = getattr(self._find_field(attr), 'only', None)
        if attr.endswith('_section_options') and only:
            options = get_value(obj, attr)
            return [[key, value] for key, value in options if key in only]
        return super().get_attribute(obj, attr, default)

    def _find_field(self, attr):
        for name, field in self.declared_fields.items():
            if name == attr or field.attribute == attr:
                return field

    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.UUID(dump_only=True)
    name = fields.String(validate=PJSIPSection())
    label = fields.String(validate=Length(max=128), allow_none=True)

    aor_section_options = OptionsField()
    auth_section_options = OptionsField()
    endpoint_section_options = OptionsField()
    identify_section_options = OptionsField()
    registration_section_options = OptionsField()
    registration_outbound_auth_section_options = OptionsField()
    outbound_auth_section_options = OptionsField()

    templates = fields.List(Nested('EndpointSIPRelationSchema'), missing=[])
    transport = Nested('TransportRelationSchema', allow_none=True)
    asterisk_id = fields.String(validate=Length(max=1024), allow_none=True)


class EndpointSIPSchema(_BaseSIPSchema):

    links = ListLink(Link('endpoint_sip', field='uuid'))

    trunk = Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
    line = Nested('LineSchema', only=['id', 'links'], dump_only=True)


class MergedEndpointSIPSchema(EndpointSIPSchema):
    aor_section_options = OptionsField(attribute='combined_aor_section_options')
    auth_section_options = OptionsField(attribute='combined_auth_section_options')
    endpoint_section_options = OptionsField(
        attribute='combined_endpoint_section_options'
    )
    identify_section_options = OptionsField(
        attribute='combined_identify_section_options'
    )
    registration_section_options = OptionsField(
        attribute='combined_registration_section_options'
    )
    registration_outbound_auth_section_options = OptionsField(
        attribute='combined_registration_outbound_auth_section_options',
    )
    outbound_auth_section_options = OptionsField(
        attribute='combined_outbound_auth_section_options'
    )

    @post_dump
    def merge_options(self, data, **kwargs):
        sections = [
            'aor',
            'auth',
            'endpoint',
            'identify',
            'registration',
            'registration_outbound_auth',
            'outbound_auth',
        ]
        for section in sections:
            combined_options = data.pop('{}_section_options'.format(section), [])
            accumulator = {}
            for key, value in combined_options:
                accumulator[key] = value
            data['{}_section_options'.format(section)] = list(accumulator.items())
        return data


class TemplateSIPSchema(_BaseSIPSchema):

    links = ListLink(Link('endpoint_sip_templates', field='uuid'))
