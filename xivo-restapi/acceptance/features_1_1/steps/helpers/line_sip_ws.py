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

from acceptance.features_1_1 import ws_utils_session as ws_utils


LINES_SIP_URL = 'lines_sip'


def all_lines():
    return ws_utils.rest_get(LINES_SIP_URL)

def get(lineid):
    return ws_utils.rest_get('%s/%s' % (LINES_SIP_URL, lineid))


def create_line_sip(parameters):
    return ws_utils.rest_post(LINES_SIP_URL, parameters)


def update(lineid, parameters):
    return ws_utils.rest_put('%s/%s' % (LINES_SIP_URL, lineid), parameters)


def delete(line_id):
    return ws_utils.rest_delete('%s/%s' % (LINES_SIP_URL, line_id))
