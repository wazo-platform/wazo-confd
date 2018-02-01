# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields, post_dump
from marshmallow.validate import OneOf, Length, Range

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink


class CallFilterRecipientsSchema(BaseSchema):
    user = fields.Nested('UserSchema',
                         only=['uuid', 'firstname', 'lastname', 'links'],
                         dump_only=True)
    timeout = fields.Integer(dump_only=True)

    @post_dump
    def merge_user(self, data):
        user = data.pop('user', {})
        if user:
            data.update(user)
        return data


class CallFilterSurrogatesSchema(BaseSchema):
    user = fields.Nested('UserSchema',
                         only=['uuid', 'firstname', 'lastname', 'links'],
                         dump_only=True)

    @post_dump
    def merge_user(self, data):
        return data.pop('user', {})


class CallFilterSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    strategy = fields.String(validate=OneOf([
        'all-recipients-then-linear-surrogates',
        'all-recipients-then-all-surrogates',
        'all-surrogates-then-all-recipients',
        'linear-surrogates-then-all-recipients',
        'all',
    ]), required=True)
    source = fields.String(validate=OneOf([
        'internal',
        'external',
        'all',
    ]), attribute='callfrom', required=True)
    caller_id_mode = fields.String(validate=OneOf([
        'prepend',
        'overwrite',
        'append',
    ]), allow_none=True)
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    surrogates_timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    description = fields.String(allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('callfilters'))

    recipients = fields.Nested('CallFilterRecipientsSchema', many=True, dump_only=True)
    surrogates = fields.Nested('CallFilterSurrogatesSchema', many=True, dump_only=True)

    @post_dump
    def wrap_users(self, data):
        recipient_users = data.pop('recipients', [])
        surrogate_users = data.pop('surrogates', [])

        if not self.only or 'recipients' in self.only:
            data['recipients'] = {'users': recipient_users}
        if not self.only or 'surrogates' in self.only:
            data['surrogates'] = {'users': surrogate_users}

        return data
