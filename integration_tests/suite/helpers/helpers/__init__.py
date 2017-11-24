# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from ..client import ConfdClient
from ..database import create_helper as db_create_helper
from ..provd import create_helper as provd_create_helper


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


import destination

import agent
import agent_login_status
import call_filter
import call_filter_entity
import call_log
import call_permission
import call_pickup
import call_pickup_entity
import conference
import conference_extension
import context_entity
import cti_profile
import device
import endpoint_custom
import endpoint_sccp
import endpoint_sip
import entity
import extension
import funckey_template
import group
import group_extension
import group_member_extension
import group_member_user
import group_schedule
import incall
import incall_extension
import incall_schedule
import incall_user
import ivr
import line
import line_device
import line_endpoint_custom
import line_endpoint_sccp
import line_endpoint_sip
import line_extension
import line_sip
import meetme
import moh
import paging
import paging_caller_user
import paging_member_user
import parking_lot
import parking_lot_extension
import outcall
import outcall_extension
import outcall_schedule
import outcall_trunk
import queue
import queue_extension
import queue_member_agent
import register_sip
import schedule
import schedule_entity
import switchboard
import switchboard_member_user
import trunk
import trunk_endpoint_custom
import trunk_endpoint_sip
import user
import user_agent
import user_call_permission
import user_cti_profile
import user_entity
import user_funckey_template
import user_import
import user_line
import user_schedule
import user_voicemail
import voicemail
import voicemail_zonemessages
