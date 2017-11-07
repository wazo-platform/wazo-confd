# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for

from xivo_dao.alchemy.voicemail import Voicemail

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import VoicemailSchema


class VoicemailList(ListResource):

    model = Voicemail
    schema = VoicemailSchema

    def build_headers(self, voicemail):
        return {'Location': url_for('voicemails', id=voicemail.id, _external=True)}

    @required_acl('confd.voicemails.create')
    def post(self):
        return super(VoicemailList, self).post()

    @required_acl('confd.voicemails.read')
    def get(self):
        return super(VoicemailList, self).get()


class VoicemailItem(ItemResource):

    schema = VoicemailSchema

    @required_acl('confd.voicemails.{id}.read')
    def get(self, id):
        return super(VoicemailItem, self).get(id)

    @required_acl('confd.voicemails.{id}.update')
    def put(self, id):
        return super(VoicemailItem, self).put(id)

    @required_acl('confd.voicemails.{id}.delete')
    def delete(self, id):
        return super(VoicemailItem, self).delete(id)
