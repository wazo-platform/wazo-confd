# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from ..client import ConfdClient
from ..database import create_helper as db_create_helper


class NewClientWrapper:
    def __init__(self):
        self.host = None
        self.port = None
        self.headers = None
        self.encoder = None
        self._client = None

    def __getattr__(self, attr):
        if self._client is None:
            self._client = self._create_client()

        # This trick is needed because the self._client.url cannot be "confd.users.import.post()"
        if attr in ['post', 'put']:
            return getattr(self._client, attr)

        return getattr(self._client.url, attr)

    def _create_client(self):
        return ConfdClient.from_options(
            host=self.host, port=self.port, headers=self.headers, encoder=self.encoder
        )


class DatabaseWrapper:
    def __init__(self):
        self.host = None
        self.port = None
        self._db = None

    def __getattr__(self, attr):
        if self._db is None:
            self._db = db_create_helper(host=self.host, port=self.port)
        return getattr(self._db, attr)


class ProvdWrapper:
    def __init__(self):
        self.host = None
        self.port = None
        self._provd = None

    def __getattr__(self, attr):
        if self._provd is None:
            from ..provd import create_helper as provd_create_helper

            self._provd = provd_create_helper(host=self.host, port=self.port)
        return getattr(self._provd, attr)


confd = NewClientWrapper()
new_client = NewClientWrapper()
db = DatabaseWrapper()
provd = ProvdWrapper()


def setup_confd(host, port):
    confd.host = host
    confd.port = port


def setup_new_client(host, port):
    new_client.host = host
    new_client.port = port


def setup_database(host, port):
    db.host = host
    db.port = port


def setup_provd(host, port):
    provd.host = host
    provd.port = port


from . import access_feature  # noqa
from . import agent  # noqa
from . import agent_login_status  # noqa
from . import agent_skill  # noqa
from . import application  # noqa
from . import call_filter  # noqa
from . import call_filter_recipient_user  # noqa
from . import call_filter_surrogate_user  # noqa
from . import call_permission  # noqa
from . import call_pickup  # noqa
from . import call_pickup_interceptor_group  # noqa
from . import call_pickup_interceptor_user  # noqa
from . import call_pickup_target_group  # noqa
from . import call_pickup_target_user  # noqa
from . import conference  # noqa
from . import conference_extension  # noqa
from . import context_context  # noqa
from . import destination  # noqa
from . import device  # noqa
from . import endpoint_custom  # noqa
from . import endpoint_iax  # noqa
from . import endpoint_sccp  # noqa
from . import endpoint_sip  # noqa
from . import extension  # noqa
from . import extension_feature  # noqa
from . import funckey_template  # noqa
from . import group  # noqa
from . import group_call_permission  # noqa
from . import group_extension  # noqa
from . import group_member_extension  # noqa
from . import group_member_user  # noqa
from . import group_schedule  # noqa
from . import incall  # noqa
from . import incall_extension  # noqa
from . import incall_schedule  # noqa
from . import incall_user  # noqa
from . import ivr  # noqa
from . import line  # noqa
from . import line_application  # noqa
from . import line_device  # noqa
from . import line_endpoint_custom  # noqa
from . import line_endpoint_sccp  # noqa
from . import line_endpoint_sip  # noqa
from . import line_extension  # noqa
from . import line_fellowship  # noqa
from . import line_sip  # noqa
from . import meetme  # noqa
from . import moh  # noqa
from . import paging  # noqa
from . import paging_caller_user  # noqa
from . import paging_member_user  # noqa
from . import parking_lot  # noqa
from . import parking_lot_extension  # noqa
from . import outcall  # noqa
from . import outcall_call_permission  # noqa
from . import outcall_extension  # noqa
from . import outcall_schedule  # noqa
from . import outcall_trunk  # noqa
from . import queue  # noqa
from . import queue_extension  # noqa
from . import queue_member_agent  # noqa
from . import queue_member_user  # noqa
from . import queue_schedule  # noqa
from . import register_iax  # noqa
from . import register_sip  # noqa
from . import registrar  # noqa
from . import sound  # noqa
from . import schedule  # noqa
from . import skill  # noqa
from . import skill_rule  # noqa
from . import switchboard  # noqa
from . import switchboard_member_user  # noqa
from . import trunk  # noqa
from . import trunk_endpoint_custom  # noqa
from . import trunk_endpoint_iax  # noqa
from . import trunk_endpoint_sip  # noqa
from . import trunk_register_iax  # noqa
from . import trunk_register_sip  # noqa
from . import user  # noqa
from . import user_agent  # noqa
from . import user_call_permission  # noqa
from . import user_funckey_template  # noqa
from . import user_import  # noqa
from . import user_line  # noqa
from . import user_schedule  # noqa
from . import user_voicemail  # noqa
from . import voicemail  # noqa
from . import voicemail_zonemessages  # noqa


__all__ = [
    'access_feature',
    'destination',
    'agent',
    'agent_login_status',
    'agent_skill',
    'application',
    'call_filter',
    'call_filter_recipient_user',
    'call_filter_surrogate_user',
    'call_permission',
    'call_pickup',
    'call_pickup_interceptor_group',
    'call_pickup_interceptor_user',
    'call_pickup_target_group',
    'call_pickup_target_user',
    'conference',
    'conference_extension',
    'context_context',
    'device',
    'endpoint_custom',
    'endpoint_iax',
    'endpoint_sccp',
    'endpoint_sip',
    'extension',
    'extension_feature',
    'funckey_template',
    'group',
    'group_call_permission',
    'group_extension',
    'group_member_extension',
    'group_member_user',
    'group_schedule',
    'incall',
    'incall_extension',
    'incall_schedule',
    'incall_user',
    'ivr',
    'line',
    'line_application',
    'line_device',
    'line_endpoint_custom',
    'line_endpoint_sccp',
    'line_endpoint_sip',
    'line_extension',
    'line_fellowship',
    'line_sip',
    'meetme',
    'moh',
    'paging',
    'paging_caller_user',
    'paging_member_user',
    'parking_lot',
    'parking_lot_extension',
    'outcall',
    'outcall_call_permission',
    'outcall_extension',
    'outcall_schedule',
    'outcall_trunk',
    'queue',
    'queue_extension',
    'queue_member_agent',
    'queue_member_user',
    'queue_schedule',
    'registrar',
    'register_iax',
    'register_sip',
    'sound',
    'schedule',
    'skill',
    'skill_rule',
    'switchboard',
    'switchboard_member_user',
    'trunk',
    'trunk_endpoint_custom',
    'trunk_endpoint_iax',
    'trunk_endpoint_sip',
    'trunk_register_iax',
    'trunk_register_sip',
    'user',
    'user_agent',
    'user_call_permission',
    'user_funckey_template',
    'user_import',
    'user_line',
    'user_schedule',
    'user_voicemail',
    'voicemail',
    'voicemail_zonemessages',
]
