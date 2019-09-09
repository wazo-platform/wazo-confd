# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink


class RegistrarSchema(BaseSchema):

    id = fields.String()
    deletable = fields.Boolean(missing=True, default=True)
    name = fields.String(allow_none=True)
    main_host = fields.String(required=True)
    main_port = fields.Integer(allow_none=True)
    backup_host = fields.String(allow_none=True)
    backup_port = fields.Integer(allow_none=True)
    proxy_main_host = fields.String(required=True)
    proxy_main_port = fields.Integer(allow_none=True)
    proxy_backup_host = fields.String(allow_none=True)
    proxy_backup_port = fields.Integer(allow_none=True)
    outbound_proxy_host = fields.String(allow_none=True)
    outbound_proxy_port = fields.Integer(allow_none=True)
    links = ListLink(Link('registrars'))
