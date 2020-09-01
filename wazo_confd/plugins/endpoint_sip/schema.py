# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from marshmallow import fields, EXCLUDE, post_dump
from marshmallow.validate import Length
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


class TemplateSIPSchema(_BaseSIPSchema):

    links = ListLink(Link('endpoint_sip_templates', field='uuid'))
