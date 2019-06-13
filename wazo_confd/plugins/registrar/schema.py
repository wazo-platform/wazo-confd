# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class RegistrarSchema(BaseSchema):

    id = fields.String()
    name = fields.String(attribute='displayname')
    main_host = fields.String(attribute='registrar_main')
    main_port = fields.Integer(attribute='registrar_main_port')
    backup_host = fields.String(attribute='registrar_backup')
    backup_port = fields.Integer(attribute='registrar_backup_port')
    proxy_main_host = fields.String(attribute='proxy_main')
    proxy_main_port = fields.Integer(attribute='proxy_main_port')
    proxy_backup_host = fields.String(attribute='proxy_backup')
    proxy_backup_port = fields.Integer(attribute='proxy_backup_port')
    outbound_proxy_host = fields.String(attribute='proxy_outbound')
    outbound_proxy_port = fields.Integer(attribute='proxy_outbound_port')
