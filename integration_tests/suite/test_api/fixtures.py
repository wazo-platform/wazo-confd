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

import helpers as h


class user(IsolatedAction):

    actions = {'generate': h.user.generate_user,
               'delete': h.user.delete_user}


class line(IsolatedAction):

    actions = {'generate': h.line.generate_line,
               'delete': h.line.delete_line}


class line_sip(IsolatedAction):

    actions = {'generate': h.line_sip.generate_line,
               'delete': h.line_sip.delete_line}


class sip(IsolatedAction):

    actions = {'generate': h.endpoint_sip.generate_sip,
               'delete': h.endpoint_sip.delete_sip}


class sccp(IsolatedAction):

    actions = {'generate': h.endpoint_sccp.generate_sccp,
               'delete': h.endpoint_sccp.delete_sccp}


class extension(IsolatedAction):

    actions = {'generate': h.extension.generate_extension,
               'delete': h.extension.delete_extension}


class device(IsolatedAction):

    actions = {'generate': h.device.generate_device,
               'delete': h.device.delete_device}


class autoprov(IsolatedAction):

    actions = {'generate': h.device.generate_autoprov,
               'delete': h.device.delete_device}


class voicemail(IsolatedAction):

    actions = {'generate': h.voicemail.generate_voicemail,
               'delete': h.voicemail.delete_voicemail}


class context(IsolatedAction):

    actions = {'generate': h.context.generate_context,
               'delete': h.context.delete_context}


class csv_entry(IsolatedAction):

    actions = {'generate': h.user_import.generate_entry}


class cti_profile(IsolatedAction):

    actions = {'generate': h.cti_profile.find_by_name}


class custom(IsolatedAction):

    actions = {'generate': h.endpoint_custom.generate_custom,
               'delete': h.endpoint_custom.delete_custom}
