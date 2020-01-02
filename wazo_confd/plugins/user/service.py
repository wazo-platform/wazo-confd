# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.func_key import dao as func_key_dao

from wazo_confd.helpers.resource import CRUDService
from wazo_confd.helpers.validator import ValidationGroup
from wazo_confd.plugins.device.builder import build_device_updater

from .validator import build_validator, build_validator_forward
from .notifier import build_notifier, build_notifier_service, build_notifier_forward


class UserBaseService(CRUDService):
    def get(self, user_id, tenant_uuids=None):
        return self.dao.get_by_id_uuid(user_id, tenant_uuids)


class UserService(UserBaseService):
    def __init__(self, dao, validator, notifier, device_updater, func_key_dao):
        super(UserService, self).__init__(dao, validator, notifier)
        self.device_updater = device_updater
        self.func_key_dao = func_key_dao

    def edit(self, user, updated_fields=None):
        super(UserService, self).edit(user, updated_fields)
        self.device_updater.update_for_user(user)

    def delete(self, user):
        self.validator.validate_delete(user)
        users = self.func_key_dao.find_users_having_user_destination(user)
        self.dao.delete(user)
        self.notifier.deleted(user)
        for user in users:
            self.device_updater.update_for_user(user)


def build_service(provd_client):
    updater = build_device_updater(provd_client)
    return UserService(
        user_dao, build_validator(), build_notifier(), updater, func_key_dao
    )


class UserCallServiceService(UserBaseService):
    def edit(self, user, schema):
        self.validator.validate_edit(user)
        self.dao.edit(user)
        self.notifier.edited(user, schema)


def build_service_callservice():
    return UserCallServiceService(user_dao, ValidationGroup(), build_notifier_service())


class UserForwardService(UserBaseService):
    def edit(self, user, schema):
        self.validator.validate_edit(user)
        self.dao.edit(user)
        self.notifier.edited(user, schema)


def build_service_forward():
    return UserForwardService(
        user_dao, build_validator_forward(), build_notifier_forward()
    )
