# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.func_key import dao as func_key_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user import strategy

from wazo_confd.helpers.resource import CRUDService
from wazo_confd.helpers.validator import ValidationGroup
from wazo_confd.plugins.device.builder import build_device_updater

from .notifier import build_notifier, build_notifier_forward, build_notifier_service
from .validator import build_validator, build_validator_forward


class UserBaseService(CRUDService):
    def get(self, user_id, tenant_uuids=None):
        return self.dao.get_by_id_uuid(user_id, tenant_uuids)


class UserService(UserBaseService):
    def __init__(
        self,
        dao,
        validator,
        notifier,
        device_updater,
        func_key_dao,
        paginated_user_strategy_threshold,
    ):
        super().__init__(dao, validator, notifier)
        self.device_updater = device_updater
        self.func_key_dao = func_key_dao
        self._paginated_user_strategy_threshold = paginated_user_strategy_threshold

    def edit(self, user, updated_fields=None):
        super().edit(user, updated_fields)
        self.device_updater.update_for_user(user)

    def delete(self, user):
        self.validator.validate_delete(user)
        users_with_fk = self.func_key_dao.find_users_having_user_destination(user)
        self.dao.delete(user)
        self.notifier.deleted(user)
        for user_with_fk in users_with_fk:
            self.device_updater.update_for_user(user_with_fk)

    def search_collated(self, parameters, tenant_uuids=None):
        limit = parameters.get('limit')
        if limit is None or limit > self._paginated_user_strategy_threshold:
            selected_strategy = strategy.user_unpaginated_strategy
        else:
            selected_strategy = strategy.no_strategy

        with self.dao.query_options(*selected_strategy):
            return self.dao.search_collated(tenant_uuids=tenant_uuids, **parameters)


def build_service(provd_client, paginated_user_strategy_threshold):
    updater = build_device_updater(provd_client)
    return UserService(
        user_dao,
        build_validator(),
        build_notifier(),
        updater,
        func_key_dao,
        paginated_user_strategy_threshold,
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
