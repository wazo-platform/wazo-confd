# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink


class RegistrarSchema(BaseSchema):

    id = fields.String()
    name = fields.String(attribute='displayname', allow_none=True)
    main_host = fields.String(attribute='registrar_main', required=True)
    main_port = fields.Integer(attribute='registrar_main_port', allow_none=True)
    backup_host = fields.String(attribute='registrar_backup', allow_none=True)
    backup_port = fields.Integer(attribute='registrar_backup_port', allow_none=True)
    proxy_main_host = fields.String(attribute='proxy_main', required=True)
    proxy_main_port = fields.Integer(attribute='proxy_main_port', allow_none=True)
    proxy_backup_host = fields.String(attribute='proxy_backup', allow_none=True)
    proxy_backup_port = fields.Integer(attribute='proxy_backup_port', allow_none=True)
    outbound_proxy_host = fields.String(attribute='proxy_outbound', allow_none=True)
    outbound_proxy_port = fields.Integer(attribute='proxy_outbound_port', allow_none=True)
    links = ListLink(Link('registrars'))
