# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from marshmallow import fields, pre_load
from marshmallow.validate import Length, OneOf

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink

logger = logging.getLogger(__name__)


class MohFileSchema(BaseSchema):
    name = fields.String()


class MohSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    label = fields.String(validate=Length(max=128), required=True)
    mode = fields.String(validate=OneOf(['custom', 'files', 'mp3']), required=True)
    application = fields.String(validate=Length(max=256), allow_none=True)
    sort = fields.String(
        validate=OneOf(['alphabetical', 'random', 'random_start']), allow_none=True
    )
    files = fields.Nested(MohFileSchema, many=True, dump_only=True)

    links = ListLink(Link('moh', field='uuid'))

    # DEPRECATED 21.15
    @pre_load
    def copy_name_to_label(self, data):
        if 'label' in data:
            return data
        if 'name' in data:
            logger.warning('the "name" field of moh is deprecated. use "label" instead')
            data['label'] = data['name']
        return data


class MohSchemaPUT(MohSchema):
    name = fields.String(dump_only=True)
