# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.plugins.user.validator import build_validator, build_validator_forward
from xivo_confd.plugins.user.notifier import build_notifier, build_notifier_service, build_notifier_forward
from xivo_confd.plugins.device.builder import build_device_updater

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.helpers.validator import ValidationGroup

from xivo_dao.resources.user import dao as user_dao


class UserBaseService(CRUDService):

    def get(self, user_id):
        return self.dao.get_by_id_uuid(user_id)


class UserService(UserBaseService):

    def __init__(self, dao, validator, notifier, device_updater):
        super(UserService, self).__init__(dao, validator, notifier)
        self.device_updater = device_updater

    def edit(self, user, updated_fields=None):
        super(UserService, self).edit(user, updated_fields)
        self.device_updater.update_for_user(user)

    def legacy_search(self, term):
        return self.dao.legacy_search(term)


def build_service(provd_client):
    updater = build_device_updater(provd_client)
    return UserService(user_dao,
                       build_validator(),
                       build_notifier(),
                       updater)


class UserCallServiceService(UserBaseService):

    def edit(self, user, schema):
        self.validator.validate_edit(user)
        self.dao.edit(user)
        self.notifier.edited(user, schema)


def build_service_callservice():
    return UserCallServiceService(user_dao,
                                  ValidationGroup(),
                                  build_notifier_service())


class UserForwardService(UserBaseService):

    def edit(self, user, schema):
        self.validator.validate_edit(user)
        self.dao.edit(user)
        self.notifier.edited(user, schema)


def build_service_forward():
    return UserForwardService(user_dao,
                              build_validator_forward(),
                              build_notifier_forward())
