# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.skill import dao as skill_dao

from xivo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class SkillService(CRUDService):

    def create(self, skill):
        self.validator.validate_create(skill, tenant_uuids=[skill.tenant_uuid])
        created_skill = self.dao.create(skill)
        self.notifier.created(created_skill)
        return created_skill

    def edit(self, skill, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(skill, tenant_uuids=[skill.tenant_uuid])
        self.dao.edit(skill)
        self.notifier.edited(skill)


def build_service():
    return SkillService(skill_dao, build_validator(), build_notifier())
