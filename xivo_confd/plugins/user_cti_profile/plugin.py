# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.cti_profile import dao as cti_profile_dao

from xivo_confd import api
from xivo_confd.plugins.user_cti_profile import service
from xivo_confd.plugins.user_cti_profile.resource import UserCtiProfileRoot


class Plugin(object):

    def load(self, core):
        api.add_resource(UserCtiProfileRoot,
                         '/users/<int:user_id>/cti',
                         '/users/<uuid:user_id>/cti',
                         endpoint='user_cti_profiles',
                         resource_class_args=(service, user_dao, cti_profile_dao)
                         )
