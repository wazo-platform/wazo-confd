# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from marshmallow import fields
from marshmallow.validate import Length, Range, Regexp

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.helpers.mallow import BaseSchema


EXTERNAL_PREFIX_REGEX = r'^\+|\+?[0-9#*]+$'
PREFIX_REGEX = r'^\+|\+?[0-9#*]+$'


class OutcallExtensionSchema(BaseSchema):
    caller_id = fields.String(validate=Length(max=80), allow_none=True)
    external_prefix = fields.String(validate=(Length(max=64), Regexp(EXTERNAL_PREFIX_REGEX)), allow_none=True)
    prefix = fields.String(validate=(Length(max=32), Regexp(PREFIX_REGEX)), allow_none=True)
    strip_digits = fields.Integer(validate=Range(min=0))


class OutcallExtensionItem(ConfdResource):

    schema = OutcallExtensionSchema

    def __init__(self, service, outcall_dao, extension_dao):
        super(OutcallExtensionItem, self).__init__()
        self.service = service
        self.outcall_dao = outcall_dao
        self.extension_dao = extension_dao

    @required_acl('confd.outcalls.{outcall_id}.extensions.{extension_id}.delete')
    def delete(self, outcall_id, extension_id):
        outcall = self.outcall_dao.get(outcall_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(outcall, extension)
        return '', 204

    @required_acl('confd.outcalls.{outcall_id}.extensions.{extension_id}.update')
    def put(self, outcall_id, extension_id):
        outcall = self.outcall_dao.get(outcall_id)
        extension = self.extension_dao.get(extension_id)
        outcall_extension = self.schema().load(request.get_json()).data
        self.service.associate(outcall, extension, outcall_extension)
        return '', 204
