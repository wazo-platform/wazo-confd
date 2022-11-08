# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.user import dao as user_dao

from wazo_confd.plugins.user_group.resource import GroupsIDUUIDSchema


class UserGroupAssociationMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = GroupsIDUUIDSchema()

    def associate_all_groups(self, body, user_id):
        form = self._schema.load(body)
        try:
            groups = [group_dao.get_by(**group) for group in form['groups']]
        except NotFoundError as e:
            raise errors.param_not_found('groups', 'Group', **e.metadata)

        self._service.associate_all_groups(
            user_dao.get_by_id_uuid(user_id),
            groups,
        )
