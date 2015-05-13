# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.resources.user_cti_profile.model import UserCtiProfile
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_cti_profile import dao

from xivo_confd.resources.user_cti_profile import validator, notifier


def get(user_id):
    cti_profile = dao.find_profile_by_userid(user_id)
    cti_profile_id = None if cti_profile is None else cti_profile.id
    enabled = user_dao.is_cti_enabled(user_id)
    return UserCtiProfile(user_id=user_id, cti_profile_id=cti_profile_id, enabled=enabled)


def edit(user_cti_profile):
    validator.validate_edit(user_cti_profile)
    dao.edit(user_cti_profile)
    notifier.edited(user_cti_profile)
