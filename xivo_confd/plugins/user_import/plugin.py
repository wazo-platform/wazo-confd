# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import OrderedDict

from xivo_dao.resources.call_permission import dao as call_permission_dao
from xivo_dao.resources.endpoint_sccp import dao as sccp_dao
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_call_permission import dao as user_call_permission_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao
from wazo_provd_client import Client as ProvdClient

from xivo_confd.database import user_export as user_export_dao
from xivo_confd.plugins.call_permission.service import build_service as build_call_permission_service
from xivo_confd.plugins.context.service import build_service as build_context_service
from xivo_confd.plugins.endpoint_sccp.service import build_service as build_sccp_service
from xivo_confd.plugins.endpoint_sip.service import build_service as build_sip_service
from xivo_confd.plugins.extension.service import build_service as build_extension_service
from xivo_confd.plugins.incall.service import build_service as build_incall_service
from xivo_confd.plugins.incall_extension.service import build_service as build_incall_extension_service
from xivo_confd.plugins.line.service import build_service as build_line_service
from xivo_confd.plugins.line_endpoint.service import build_service as build_le_service
from xivo_confd.plugins.line_extension.service import build_service as build_line_extension_service
from xivo_confd.plugins.user.service import build_service as build_user_service
from xivo_confd.plugins.user_call_permission.service import build_service as build_user_call_permission_service
from xivo_confd.plugins.user_line.service import build_service as build_ul_service
from xivo_confd.plugins.user_voicemail.service import build_service as build_uv_service
from xivo_confd.plugins.voicemail.service import build_service as build_voicemail_service

from .associators import (
    CallPermissionAssociator,
    ExtensionAssociator,
    IncallAssociator,
    LineAssociator,
    SccpAssociator,
    SipAssociator,
    VoicemailAssociator,
    WazoUserAssociator,
)
from .creators import (
    CallPermissionCreator,
    ContextCreator,
    ExtensionCreator,
    IncallCreator,
    LineCreator,
    SccpCreator,
    SipCreator,
    UserCreator,
    VoicemailCreator,
    WazoUserCreator,
)
from .entry import EntryCreator, EntryAssociator, EntryFinder, EntryUpdater
from .resource import UserImportResource, UserExportResource
from .service import ImportService, ExportService
from .wazo_user_service import build_service as build_wazo_user_service
from .auth_client import set_auth_client_config, auth_client


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        set_auth_client_config(config['auth'])

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        user_service = build_user_service(provd_client)
        wazo_user_service = build_wazo_user_service()
        user_voicemail_service = build_uv_service()
        voicemail_service = build_voicemail_service()
        line_service = build_line_service(provd_client)
        sip_service = build_sip_service(provd_client)
        sccp_service = build_sccp_service()
        line_sip_service = build_le_service(provd_client, 'sip', sip_service)
        line_sccp_service = build_le_service(provd_client, 'sccp', sccp_service)
        extension_service = build_extension_service(provd_client)
        user_line_service = build_ul_service()
        line_extension_service = build_line_extension_service()
        call_permission_service = build_call_permission_service()
        user_call_permission_service = build_user_call_permission_service()
        incall_service = build_incall_service()
        incall_extension_service = build_incall_extension_service()
        context_service = build_context_service()

        creators = {
            'user': UserCreator(user_service),
            'wazo_user': WazoUserCreator(wazo_user_service),
            'line': LineCreator(line_service),
            'voicemail': VoicemailCreator(voicemail_service),
            'sip': SipCreator(sip_service),
            'sccp': SccpCreator(sccp_service),
            'extension': ExtensionCreator(extension_service),
            'extension_incall': ExtensionCreator(extension_service),
            'incall': IncallCreator(incall_service),
            'call_permissions': CallPermissionCreator(call_permission_service),
            'context': ContextCreator(context_service),
        }

        entry_creator = EntryCreator(creators)

        associators = OrderedDict([
            ('wazo_user', WazoUserAssociator(wazo_user_service)),
            ('voicemail', VoicemailAssociator(user_voicemail_service)),
            ('sip', SipAssociator(line_sip_service)),
            ('sccp', SccpAssociator(line_sccp_service)),
            ('line', LineAssociator(user_line_service)),
            ('extension', ExtensionAssociator(line_extension_service)),
            ('incall', IncallAssociator(incall_extension_service)),
            ('call_permissions', CallPermissionAssociator(user_call_permission_service,
                                                          call_permission_service)),
        ])

        entry_associator = EntryAssociator(associators)

        entry_finder = EntryFinder(
            user_dao,
            voicemail_dao,
            user_voicemail_dao,
            line_dao,
            user_line_dao,
            line_extension_dao,
            sip_dao,
            sccp_dao,
            extension_dao,
            incall_dao,
            call_permission_dao,
            user_call_permission_dao
        )

        entry_updater = EntryUpdater(creators, associators, entry_finder)

        import_service = ImportService(entry_creator, entry_associator, entry_updater)
        api.add_resource(
            UserImportResource,
            '/users/import',
            resource_class_args=(import_service,),
        )

        export_service = ExportService(user_export_dao, auth_client)
        api.add_resource(
            UserExportResource,
            '/users/export',
            resource_class_args=(export_service,)
        )
