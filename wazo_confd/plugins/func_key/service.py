# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.func_key_template import dao as template_dao_module
from xivo_dao.resources.user import dao as user_dao_module

from wazo_confd.plugins.device import builder as device_builder

from .notifier import build_notifier
from .validator import (
    build_user_template_validator,
    build_validator,
    build_validator_bsfilter,
)


class TemplateService:
    DESTINATION_BLFS = (
        'agent',
        'bsfilter',
        'conference',
        'custom',
        'forward',
        'groupmember',
        'park_position',
        'user',
    )

    SERVICE_BLFS = ('callrecord', 'enablednd', 'enablevm', 'incallfilter')

    def __init__(
        self,
        template_dao,
        user_dao,
        validator,
        validator_bsfilter,
        notifier,
        device_updater,
    ):
        self.template_dao = template_dao
        self.user_dao = user_dao
        self.validator = validator
        self.notifier = notifier
        self.device_updater = device_updater
        self.validator_bsfilter = validator_bsfilter

    def get(self, template_id, tenant_uuids=None):
        return self.template_dao.get(template_id, tenant_uuids=tenant_uuids)

    def get_unified_template(self, user_id, tenant_uuids=None):
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        if user.func_key_template_id:
            public_template = self.get(user.func_key_template_id)
            private_template = self.get(user.private_template_id)
            return public_template.merge(private_template)
        else:
            return self.get(user.private_template_id)

    def search(self, parameters, tenant_uuids):
        return self.template_dao.search(tenant_uuids=tenant_uuids, **parameters)

    def create(self, template):
        self.validator.validate_create(template, tenant_uuids=[template.tenant_uuid])
        self._adjust_blfs(template)
        created_template = self.template_dao.create(template)
        self.notifier.created(created_template)
        return created_template

    def edit(self, template, updated_fields=None):
        self.validator.validate_edit(template, tenant_uuids=[template.tenant_uuid])
        self._adjust_blfs(template)
        self.template_dao.edit(template)
        self.device_updater.update_for_template(template)
        self.notifier.edited(template, updated_fields)

    def edit_funckey(self, funckey, template, position):
        template.keys[position] = funckey
        updated_fields = [position]
        self.edit(template, updated_fields)

    def edit_user_funckey(self, user, funckey, template, position):
        self.validator_bsfilter.validate(user, funckey)
        self.edit_funckey(funckey, template, position)

    def edit_user_template(self, user, template, updated_fields):
        for funckey in template.keys.values():
            self.validator_bsfilter.validate(user, funckey)
        self.edit(template, updated_fields)

    def delete(self, template):
        self.validator.validate_delete(template, tenant_uuids=[template.tenant_uuid])
        users = self.user_dao.find_all_by(func_key_template_id=template.id)
        self.template_dao.delete(template)
        for user in users:
            Session.expire(user, ['func_key_template_id'])
            self.device_updater.update_for_user(user)
        self.notifier.deleted(template)

    def delete_funckey(self, template, position):
        if position in template.keys:
            del template.keys[position]
        updated_fields = [position]
        self.edit(template, updated_fields)

    def _adjust_blfs(self, template):
        for funckey in template.keys.values():
            destination = funckey.destination
            if destination.type == 'service':
                if destination.service not in self.SERVICE_BLFS:
                    funckey.blf = False
            elif destination.type not in self.DESTINATION_BLFS:
                funckey.blf = False


def build_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)

    return TemplateService(
        template_dao_module,
        user_dao_module,
        build_validator(),
        build_validator_bsfilter(),
        build_notifier(),
        device_updater,
    )


class UserFuncKeyTemplateService:
    def __init__(self, user_dao, validator, notifier, device_updater):
        self.user_dao = user_dao
        self.validator = validator
        self.notifier = notifier
        self.device_updater = device_updater

    def find_all_by_template_id(self, template_id):
        return self.user_dao.find_all_by(func_key_template_id=template_id)

    def find_all_by_user_id(self, user_id):
        user = self.user_dao.get(user_id=user_id)
        return [user] if user.func_key_template_id else []

    def associate(self, user, template):
        self.validator.validate_association(user, template)
        user.func_key_template_id = template.id
        self.user_dao.edit(user)
        self.device_updater.update_for_user(user)

    def dissociate(self, user, template):
        if user.func_key_template_id != template.id:
            return

        self.validator.validate_dissociation(user, template)
        user.func_key_template_id = None
        self.user_dao.edit(user)
        self.device_updater.update_for_user(user)


def build_user_funckey_template_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)

    return UserFuncKeyTemplateService(
        user_dao_module,
        build_user_template_validator(),
        build_notifier(),
        device_updater,
    )
