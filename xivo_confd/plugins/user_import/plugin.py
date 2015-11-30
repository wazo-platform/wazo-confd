# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_confd import api

from xivo_confd.plugins.user.service import build_service as build_user_service
from xivo_confd.plugins.line.service import build_service as build_line_service
from xivo_confd.plugins.endpoint_sip.service import build_service as build_sip_service
from xivo_confd.plugins.endpoint_sccp.service import build_service as build_sccp_service
from xivo_confd.plugins.line_endpoint.service import build_service as build_le_service
from xivo_confd.plugins.user_import.service import ImportService
from xivo_confd.plugins.user_import.resource import UserImportResource
from xivo_confd.plugins.user_line.service import build_service as build_ul_service

from xivo_confd.plugins.line_extension import service as line_extension_service

from xivo_confd.resources.user_voicemail.services import build_service as build_uv_service
from xivo_confd.resources.voicemails.services import build_service as build_voicemail_service
from xivo_confd.resources.extensions.services import build_service as build_extension_service
from xivo_confd.resources.user_cti_profile import services as user_cti_profile_service

from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.cti_profile import dao as cti_profile_dao


class Plugin(object):

    def load(self, core):
        provd_client = core.provd_client()

        user_service = build_user_service()
        user_voicemail_service = build_uv_service()
        voicemail_service = build_voicemail_service()
        line_service = build_line_service(provd_client)
        sip_service = build_sip_service(provd_client)
        sccp_service = build_sccp_service()
        line_sip_service = build_le_service(provd_client, 'sip', sip_service)
        line_sccp_service = build_le_service(provd_client, 'sccp', sccp_service)
        extension_service = build_extension_service()
        user_line_service = build_ul_service()

        service = ImportService(user_service,
                                voicemail_service,
                                user_voicemail_service,
                                line_service,
                                sip_service,
                                sccp_service,
                                line_sip_service,
                                line_sccp_service,
                                extension_service,
                                line_extension_service,
                                user_line_service,
                                incall_dao,
                                cti_profile_dao,
                                user_cti_profile_service)

        api.add_resource(UserImportResource,
                         '/users/import',
                         resource_class_args=(service,)
                         )
