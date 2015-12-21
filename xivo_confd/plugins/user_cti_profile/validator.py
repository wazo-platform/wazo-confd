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

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.cti_profile import dao as cti_profile_dao
from xivo_dao.resources.user import dao as user_dao


def validate_edit(user_cti_profile):
    _validate_user_exists(user_cti_profile)
    if user_cti_profile.cti_profile_id:
        _validate_cti_profile_exists(user_cti_profile)
    _validate_user_has_login_passwd(user_cti_profile)


def _validate_cti_profile_exists(user_cti_profile):
    try:
        cti_profile_dao.get(user_cti_profile.cti_profile_id)
    except NotFoundError:
        raise errors.param_not_found('cti_profile_id', 'CtiProfile')


def _validate_user_exists(user_cti_profile):
    try:
        user_dao.get(user_cti_profile.user_id)
    except NotFoundError:
        raise errors.param_not_found('user_id', 'User')


def _validate_user_has_login_passwd(user_cti_profile):
    if user_cti_profile.enabled:
        user = user_dao.get(user_cti_profile.user_id)
        if not user.username or not user.password:
            raise errors.missing_cti_parameters(user_id=user.id)
