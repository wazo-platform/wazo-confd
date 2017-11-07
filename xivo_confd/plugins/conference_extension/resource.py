# -*- coding: UTF-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class ConferenceExtensionItem(ConfdResource):

    def __init__(self, service, conference_dao, extension_dao):
        super(ConferenceExtensionItem, self).__init__()
        self.service = service
        self.conference_dao = conference_dao
        self.extension_dao = extension_dao

    @required_acl('confd.conferences.{conference_id}.extensions.{extension_id}.delete')
    def delete(self, conference_id, extension_id):
        conference = self.conference_dao.get(conference_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(conference, extension)
        return '', 204

    @required_acl('confd.conferences.{conference_id}.extensions.{extension_id}.update')
    def put(self, conference_id, extension_id):
        conference = self.conference_dao.get(conference_id)
        extension = self.extension_dao.get(extension_id)
        self.service.associate(conference, extension)
        return '', 204
