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

from flask.helpers import url_for

# mapping = {model_field: api_field}
MAPPING = {
    'id': 'id',
    'user_id': 'user_id',
    'extension_id': 'extension_id',
    'line_id': 'line_id',
    'main_user': 'main_user',
    'main_line': 'main_line'
}


def add_links_to_dict(ule_dict, ule):
    ule_location = url_for('user_links.get', uleid=ule.id, _external=True)
    user_location = url_for('users.get', userid=ule.user_id, _external=True)
    line_location = url_for('lines.get', lineid=ule.line_id, _external=True)
    extension_location = url_for('extensions.get', extensionid=ule.extension_id, _external=True)
    ule_dict.update({
        'links': [
            {
                'rel': 'user_links',
                'href': ule_location
            },
            {
                'rel': 'users',
                'href': user_location
            },
            {
                'rel': 'lines',
                'href': line_location
            },
            {
                'rel': 'extensions',
                'href': extension_location
            }
        ]
    })
