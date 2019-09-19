# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from ..client import ConfdClient
from ..database import create_helper as db_create_helper

from . import access_feature
from . import agent
from . import agent_login_status
from . import agent_skill
from . import application
from . import call_filter
from . import call_filter_recipient_user
from . import call_filter_surrogate_user
from . import call_permission
from . import call_pickup
from . import call_pickup_interceptor_group
from . import call_pickup_interceptor_user
from . import call_pickup_target_group
from . import call_pickup_target_user
from . import conference
from . import conference_extension
from . import context_context
from . import destination
from . import device
from . import endpoint_custom
from . import endpoint_iax
from . import endpoint_sccp
from . import endpoint_sip
from . import extension
from . import extension_feature
from . import funckey_template
from . import group
from . import group_call_permission
from . import group_extension
from . import group_member_extension
from . import group_member_user
from . import group_schedule
from . import incall
from . import incall_extension
from . import incall_schedule
from . import incall_user
from . import ivr
from . import line
from . import line_application
from . import line_device
from . import line_endpoint_custom
from . import line_endpoint_sccp
from . import line_endpoint_sip
from . import line_extension
from . import line_fellowship
from . import line_sip
from . import meetme
from . import moh
from . import paging
from . import paging_caller_user
from . import paging_member_user
from . import parking_lot
from . import parking_lot_extension
from . import outcall
from . import outcall_call_permission
from . import outcall_extension
from . import outcall_schedule
from . import outcall_trunk
from . import queue
from . import queue_extension
from . import queue_member_agent
from . import queue_member_user
from . import queue_schedule
from . import register_iax
from . import register_sip
from . import registrar
from . import sound
from . import schedule
from . import skill
from . import skill_rule
from . import switchboard
from . import switchboard_member_user
from . import trunk
from . import trunk_endpoint_custom
from . import trunk_endpoint_iax
from . import trunk_endpoint_sip
from . import trunk_register_iax
from . import trunk_register_sip
from . import user
from . import user_agent
from . import user_call_permission
from . import user_funckey_template
from . import user_import
from . import user_line
from . import user_schedule
from . import user_voicemail
from . import voicemail
from . import voicemail_zonemessages

__all__ = [
    'access_feature',
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
    'destination',
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
    'register_iax',
    'register_sip',
    'registrar',
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
        return ConfdClient.from_options(host=self.host,
                                        port=self.port,
                                        headers=self.headers,
                                        encoder=self.encoder)


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
