# -*- coding: utf-8 -*-
#
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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


def validate_edit(user, cti_profile_id):
    if cti_profile_id is not None:
        _validate_cti_profile_exists(cti_profile_id)
    _validate_user_has_login_passwd(user)


def _validate_cti_profile_exists(cti_profile_id):
    try:
        cti_profile_dao.get(cti_profile_id)
    except NotFoundError:
        raise errors.param_not_found('cti_profile_id', 'CtiProfile')


def _validate_user_has_login_passwd(user):
    if user.cti_enabled:
        if not user.username or not user.password:
            raise errors.missing_cti_parameters(user_id=user.id)
