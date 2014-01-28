# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import url_for


MAPPING = {
    'cti_profile_id': 'cti_profile_id',
    'user_id': 'user_id'
}


def add_links_to_dict(result_dict, user_cti_profile):
    user_location = url_for('users.get', userid=user_cti_profile.user_id, _external=True)
    cti_profile_location = url_for('cti_profiles.get', cti_profile_id=user_cti_profile.cti_profile_id, _external=True)
    result_dict.update({
        'links': [
            {
                'rel': 'cti_profiles',
                'href': cti_profile_location
            },
            {
                'rel': 'users',
                'href': user_location
            },
        ]
    })
