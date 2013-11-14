# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from flask import helpers as flask_helpers

# mapping = {model_field: api_field}
MAPPING = {
    'id': 'id',
    'firstname': 'firstname',
    'lastname': 'lastname',
    'caller_id': 'caller_id',
    'outgoing_caller_id': 'outgoing_caller_id',
    'username': 'username',
    'password': 'password',
    'music_on_hold': 'music_on_hold',
    'mobile_phone_number': 'mobile_phone_number',
    'userfield': 'userfield',
    'timezone': 'timezone',
    'language': 'language',
    'description': 'description',
    'preprocess_subroutine': 'preprocess_subroutine',
}


def add_links_to_dict(user_dict, user):
    user_location = flask_helpers.url_for('.get', userid=user.id, _external=True)
    user_dict.update({
        'links': [
            {
                'rel': 'users',
                'href': user_location
            }
        ]
    })
