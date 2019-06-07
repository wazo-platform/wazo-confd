# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.restful import ListResource


class SoundLanguageSchema(BaseSchema):
    tag = fields.String(dump_only=True)


class SoundLanguageList(ListResource):

    schema = SoundLanguageSchema

    @required_acl('confd.sounds.languages.get')
    def get(self):
        return super(SoundLanguageList, self).get()

    def post(self, id):
        return '', 405
