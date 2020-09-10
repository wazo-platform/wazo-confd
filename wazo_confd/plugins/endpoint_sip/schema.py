# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from marshmallow import fields, EXCLUDE, post_dump
from marshmallow.validate import Length, OneOf
from marshmallow.utils import get_value

from wazo_confd.helpers.mallow import (
    BaseSchema,
    Link,
    ListLink,
    PJSIPSection,
    PJSIPSectionOption,
)

logger = logging.getLogger(__name__)

options_field = fields.List(
    PJSIPSectionOption(option_regex=None), missing=[], validate=Length(max=512),
)


class GETQueryStringSchema(BaseSchema):
    view = fields.String(validate=OneOf(['merged']), missing=None)


class EndpointSIPRelationSchema(BaseSchema):
    uuid = fields.UUID(required=True)


class TransportRelationSchema(BaseSchema):
    uuid = fields.UUID(required=True)


class _BaseSIPSchema(BaseSchema):
    def get_attribute(self, obj, attr, default):
        only = getattr(self.declared_fields[attr], 'only', None)
        if attr.endswith('_section_options') and only:
            options = get_value(obj, attr)
            return [[key, value] for key, value in options if key in only]
        return super().get_attribute(obj, attr, default)

    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.UUID(dump_only=True)
    name = fields.String(validate=PJSIPSection())
    label = fields.String(validate=Length(max=128), allow_none=True)

    aor_section_options = options_field
    auth_section_options = options_field
    endpoint_section_options = options_field
    identify_section_options = options_field
    registration_section_options = options_field
    registration_outbound_auth_section_options = options_field
    outbound_auth_section_options = options_field

    templates = fields.List(
        fields.Nested('EndpointSIPRelationSchema', unknown=EXCLUDE), missing=[]
    )
    transport = fields.Nested(
        'TransportRelationSchema', unknown=EXCLUDE, allow_none=True
    )
    asterisk_id = fields.String(validate=Length(max=1024), allow_none=True)


class EndpointSIPSchema(_BaseSIPSchema):

    links = ListLink(Link('endpoint_sip', field='uuid'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)


class MergedEndpointSIPSchema(BaseSchema):
    def get_attribute(self, obj, attr, default):
        only = getattr(self.declared_fields[attr], 'only', None)
        if attr.endswith('_section_options') and only:
            options = get_value(obj, attr)
            return [[key, value] for key, value in options if key in only]
        return super().get_attribute(obj, attr, default)

    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.UUID(dump_only=True)
    name = fields.String(validate=PJSIPSection())
    label = fields.String(validate=Length(max=128), allow_none=True)

    combined_aor_section_options = options_field
    combined_auth_section_options = options_field
    combined_endpoint_section_options = options_field
    combined_identify_section_options = options_field
    combined_registration_section_options = options_field
    combined_registration_outbound_auth_section_options = options_field
    combined_outbound_auth_section_options = options_field

    templates = fields.List(
        fields.Nested('EndpointSIPRelationSchema', unknown=EXCLUDE), missing=[]
    )
    transport = fields.Nested(
        'TransportRelationSchema', unknown=EXCLUDE, allow_none=True
    )
    asterisk_id = fields.String(validate=Length(max=1024), allow_none=True)

    links = ListLink(Link('endpoint_sip', field='uuid'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)

    @post_dump
    def merge_options(self, data):
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
            combined_options = data.pop('combined_{}_section_options'.format(section))
            accumulator = {}
            for key, value in combined_options:
                accumulator[key] = value
            data['{}_section_options'.format(section)] = list(accumulator.items())
        return data


class TemplateSIPSchema(_BaseSIPSchema):

    links = ListLink(Link('endpoint_sip_templates', field='uuid'))
