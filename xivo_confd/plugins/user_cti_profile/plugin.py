# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.cti_profile import dao as cti_profile_dao

from xivo_confd import api

from . import service
from .resource import UserCtiProfileRoot


class Plugin(object):

    def load(self, core):
        api.add_resource(
            UserCtiProfileRoot,
            '/users/<int:user_id>/cti',
            '/users/<uuid:user_id>/cti',
            endpoint='user_cti_profiles',
            resource_class_args=(service, user_dao, cti_profile_dao)
        )
