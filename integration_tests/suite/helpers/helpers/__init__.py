# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from ..client import ConfdClient
from ..database import create_helper as db_create_helper


class NewClientWrapper(object):

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


class DatabaseWrapper(object):

    def __init__(self):
        self.host = None
        self.port = None
        self._db = None

    def __getattr__(self, attr):
        if self._db is None:
            self._db = db_create_helper(host=self.host, port=self.port)
        return getattr(self._db, attr)


class ProvdWrapper(object):

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


from . import destination

from . import agent
from . import agent_login_status
from . import call_filter
from . import call_filter_entity
from . import call_log
from . import call_permission
from . import call_pickup
from . import call_pickup_entity
from . import conference
from . import conference_extension
from . import context_entity
from . import cti_profile
from . import device
from . import endpoint_custom
from . import endpoint_iax
from . import endpoint_sccp
from . import endpoint_sip
from . import entity
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
from . import line_device
from . import line_endpoint_custom
from . import line_endpoint_sccp
from . import line_endpoint_sip
from . import line_extension
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
from . import register_iax
from . import register_sip
from . import sound
from . import schedule
from . import schedule_entity
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
from . import user_cti_profile
from . import user_entity
from . import user_funckey_template
from . import user_import
from . import user_line
from . import user_schedule
from . import user_voicemail
from . import voicemail
from . import voicemail_zonemessages

__all__ = [
    'destination',

    'agent',
    'agent_login_status',
    'call_filter',
    'call_filter_entity',
    'call_log',
    'call_permission',
    'call_pickup',
    'call_pickup_entity',
    'conference',
    'conference_extension',
    'context_entity',
    'cti_profile',
    'device',
    'endpoint_custom',
    'endpoint_iax',
    'endpoint_sccp',
    'endpoint_sip',
    'entity',
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
    'line_device',
    'line_endpoint_custom',
    'line_endpoint_sccp',
    'line_endpoint_sip',
    'line_extension',
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
    'register_iax',
    'register_sip',
    'sound',
    'schedule',
    'schedule_entity',
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
    'user_cti_profile',
    'user_entity',
    'user_funckey_template',
    'user_import',
    'user_line',
    'user_schedule',
    'user_voicemail',
    'voicemail',
    'voicemail_zonemessages',
]
