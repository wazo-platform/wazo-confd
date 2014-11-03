# -*- coding: UTF-8 -*-
#
# Copyright (C) 2014 Avencall
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

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int
from xivo_confd.helpers.mooltiparse.errors import ValidationError


class ErrorViewNotExist(ValidationError):

    def __init__(self, error):
        Exception.__init__(self, error)
        self.error = error


def user_location(model):
    return {
        'links': [
            {
                'rel': 'users',
                'href': flask_helpers.url_for('users.get', userid=model.id, _external=True)
            }
        ]
    }

user_document = content_parser.document(
    Field('id', Int()),
    Field('firstname', Unicode()),
    Field('lastname', Unicode()),
    Field('caller_id', Unicode()),
    Field('outgoing_caller_id', Unicode()),
    Field('username', Unicode()),
    Field('password', Unicode()),
    Field('music_on_hold', Unicode()),
    Field('mobile_phone_number', Unicode()),
    Field('userfield', Unicode()),
    Field('timezone', Unicode()),
    Field('language', Unicode()),
    Field('description', Unicode()),
    Field('preprocess_subroutine', Unicode())
)


def user_directory_location(model):
    res = user_location(model)
    if model.line_id:
        res['links'].append(
            {
                'rel': 'lines',
                'href': flask_helpers.url_for('lines.get', lineid=model.line_id, _external=True)
            }
        )
    return res

user_directory_document = content_parser.document(
    Field('id', Int()),
    Field('line_id', Int()),
    Field('agent_id', Int()),
    Field('firstname', Unicode()),
    Field('lastname', Unicode()),
    Field('exten', Unicode()),
    Field('mobile_phone_number', Unicode())
)
