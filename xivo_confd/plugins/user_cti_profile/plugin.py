# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.cti_profile import dao as cti_profile_dao

from .resource import UserCtiProfileRoot
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserCtiProfileRoot,
            '/users/<int:user_id>/cti',
            '/users/<uuid:user_id>/cti',
            endpoint='user_cti_profiles',
            resource_class_args=(service, user_dao, cti_profile_dao)
        )
