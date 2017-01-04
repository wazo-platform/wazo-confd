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

from xivo_dao.helpers.db_manager import Session

from xivo_confd.plugins.user_cti_profile import validator, notifier


def edit(user, form):
    cti_profile_id = form.get('cti_profile_id', None)
    cti_enabled = form.get('cti_enabled', None)
    if cti_enabled is not None:
        user.cti_enabled = cti_enabled

    with Session.no_autoflush:
        validator.validate_edit(user, cti_profile_id)

    if cti_profile_id is not None:
        user.cti_profile_id = cti_profile_id

    notifier.edited(user)
