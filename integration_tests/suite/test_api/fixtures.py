# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from wrappers import IsolatedAction

from helpers import line, line_sip, endpoint_sip, endpoint_sccp, endpoint_custom
from helpers.user import generate_user, delete_user
from helpers.extension import generate_extension, delete_extension
from helpers.device import generate_device, delete_device
from helpers.voicemail import generate_voicemail, delete_voicemail
from helpers.context import generate_context, delete_context
from helpers import user_import
from helpers.cti_profile import find_by_name


class user(IsolatedAction):

    actions = {'generate': generate_user,
               'delete': delete_user}


class line(IsolatedAction):

    actions = {'generate': line.generate_line,
               'delete': line.delete_line}


class line_sip(IsolatedAction):

    actions = {'generate': line_sip.generate_line,
               'delete': line_sip.delete_line}


class sip(IsolatedAction):

    actions = {'generate': endpoint_sip.generate_sip,
               'delete': endpoint_sip.delete_sip}


class sccp(IsolatedAction):

    actions = {'generate': endpoint_sccp.generate_sccp,
               'delete': endpoint_sccp.delete_sccp}


class extension(IsolatedAction):

    actions = {'generate': generate_extension,
               'delete': delete_extension}


class device(IsolatedAction):

    actions = {'generate': generate_device,
               'delete': delete_device}


class voicemail(IsolatedAction):

    actions = {'generate': generate_voicemail,
               'delete': delete_voicemail}


class context(IsolatedAction):

    actions = {'generate': generate_context,
               'delete': delete_context}


class csv_entry(IsolatedAction):

    actions = {'generate': user_import.generate_entry}


class cti_profile(IsolatedAction):

    actions = {'generate': find_by_name}


class custom(IsolatedAction):

    actions = {'generate': endpoint_custom.generate_custom,
               'delete': endpoint_custom.delete_custom}
