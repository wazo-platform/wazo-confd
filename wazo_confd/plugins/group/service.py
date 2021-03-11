# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from uuid import uuid4

from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.tenant import dao as tenant_dao

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class GroupService(CRUDService):
    group_name_fmt = 'grp-{tenant_slug}-{group_uuid}'

    def __init__(self, group_dao, tenant_dao, validator, notifier):
        self._tenant_dao = tenant_dao
        super().__init__(group_dao, validator, notifier)

    def update_form(self, form):
        tenant = self._tenant_dao.get(form['tenant_uuid'])
        form['uuid'] = uuid4()
        form['name'] = self.group_name_fmt.format(
            tenant_slug=tenant.slug,
            group_uuid=form['uuid'],
        )
        return super().update_form(form)


def build_service():
    return GroupService(group_dao, tenant_dao, build_validator(), build_notifier())
