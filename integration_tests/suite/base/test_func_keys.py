# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    contains,
    empty,
    has_entries,
    has_entry,
    has_key,
    is_not,
    not_,
)

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import helpers
from ..helpers import helpers as h
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd, db, provd

FAKE_ID = 999999999

invalid_destinations = [
    1234,
    'string',
    {'type': 'invalid'},
    {'type': 'agent'},
    {'type': 'agent', 'agent_id': 'invalid'},
    {'type': 'agent', 'agent_id': None},
    {'type': 'bsfilter'},
    {'type': 'bsfilter', 'filter_member_id': 'invalid'},
    {'type': 'bsfilter', 'filter_member_id': None},
    {'type': 'conference'},
    {'type': 'conference', 'bad_field': 123},
    {'type': 'conference', 'conference_id': 'string'},
    {'type': 'conference', 'conference_id': None},
    {'type': 'custom'},
    {'type': 'custom', 'bad_field': '123'},
    {'type': 'custom', 'exten': 1234},
    {'type': 'custom', 'exten': True},
    {'type': 'custom', 'exten': None},
    {'type': 'forward'},
    {'type': 'forward', 'bad_field': 'busy'},
    {'type': 'forward', 'forward': 'invalid'},
    {'type': 'forward', 'forward': True},
    {'type': 'forward', 'forward': None},
    {'type': 'forward', 'forward': 1234},
    {'type': 'forward', 'forward': 'busy', 'exten': True},
    {'type': 'forward', 'forward': 'busy', 'exten': 1234},
    {'type': 'group'},
    {'type': 'group', 'bad_field': 123},
    {'type': 'group', 'group_id': 'string'},
    {'type': 'group', 'group_id': None},
    {'type': 'groupmember'},
    {'type': 'groupmember', 'action': 'join', 'bad_field': 123},
    {'type': 'groupmember', 'action': 'join', 'group_id': 'string'},
    {'type': 'groupmember', 'action': 'join', 'group_id': None},
    {'type': 'groupmember', 'action': 123, 'group_id': 123},
    {'type': 'groupmember', 'action': None, 'group_id': 123},
    {'type': 'groupmember', 'action': 'unknown', 'group_id': 123},
    {'type': 'paging'},
    {'type': 'paging', 'bad_field': 123},
    {'type': 'paging', 'paging_id': 'invalid'},
    {'type': 'paging', 'paging_id': None},
    {'type': 'park_position'},
    {'type': 'park_position', 'bad_field': 123},
    {'type': 'park_position', 'parking_lot_id': None, 'position': '801'},
    {'type': 'park_position', 'parking_lot_id': 'invalid', 'position': '801'},
    {'type': 'park_position', 'parking_lot_id': 123, 'position': 'invalid'},
    {'type': 'park_position', 'parking_lot_id': 123, 'position': None},
    {'type': 'parking'},
    {'type': 'parking', 'bad_field': 123},
    {'type': 'parking', 'parking_lot_id': 'string'},
    {'type': 'parking', 'parking_lot_id': None},
    {'type': 'queue'},
    {'type': 'queue', 'bad_field': 123},
    {'type': 'queue', 'queue_id': 'string'},
    {'type': 'queue', 'queue_id': None},
    {'type': 'service'},
    {'type': 'service', 'bad_field': 'enablevm'},
    {'type': 'service', 'service': 'invalid'},
    {'type': 'service', 'service': True},
    {'type': 'service', 'service': None},
    {'type': 'service', 'service': 1234},
    {'type': 'transfer'},
    {'type': 'transfer', 'bad_field': 'blind'},
    {'type': 'transfer', 'transfer': 'invalid'},
    {'type': 'transfer', 'transfer': True},
    {'type': 'transfer', 'transfer': None},
    {'type': 'transfer', 'transfer': 1234},
    {'type': 'user'},
    {'type': 'user', 'bad_field': 123},
    {'type': 'user', 'user_id': 'string'},
    {'type': 'user', 'user_id': None},
]


def error_funckey_checks(url):
    s.check_bogus_field_returns_error(url, 'blf', 123)
    s.check_bogus_field_returns_error(url, 'blf', 'string')
    s.check_bogus_field_returns_error(url, 'blf', None)
    s.check_bogus_field_returns_error(url, 'label', 1234)

    for destination in invalid_destinations:
        s.check_bogus_field_returns_error(url, 'destination', destination)


def error_funckeys_checks(url):
    valid_funckey = {'destination': {'type': 'custom', 'exten': '1234'}}

    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'keys', True)
    s.check_bogus_field_returns_error(url, 'keys', None)
    s.check_bogus_field_returns_error(url, 'keys', 'string')
    s.check_bogus_field_returns_error(url, 'keys', 1234)
    s.check_bogus_field_returns_error(url, 'keys', {'not_integer': valid_funckey})
    s.check_bogus_field_returns_error(url, 'keys', {None: valid_funckey})

    regex = r'keys.*1.*destination'
    for destination in invalid_destinations:
        s.check_bogus_field_returns_error_matching_regex(
            url, 'keys', {'1': {'destination': destination}}, regex
        )

    regex = r'keys.*1'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'keys', {'1': 'string'}, regex
    )
    s.check_bogus_field_returns_error_matching_regex(url, 'keys', {'1': 1234}, regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'keys', {'1': True}, regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'keys', {'1': None}, regex)


class BaseTestFuncKey(unittest.TestCase):
    def setUp(self):
        self.db = db
        self.provd = provd
        self.provd.reset()

        self.db.recreate()

        self.user = helpers.user.generate_user()
        self.device = self.setup_device(self.user['id'], '1000')

    def setup_device(self, user_id, exten):
        line = helpers.line_sip.generate_line_sip()
        extension = helpers.extension.add_extension(exten=exten, context='default')
        device = helpers.device.generate_device()

        helpers.user_line.associate(self.user['id'], line['id'])
        helpers.line_extension.associate(line['id'], extension['id'])
        helpers.line_device.associate(line['id'], device['id'])

        return device

    def check_provd_has_funckey(self, pos, funckey):
        config = self.provd.configs.get(self.device['id'])
        funckeys = config['raw_config']['funckeys']

        assert_that(funckeys, has_key(pos))
        assert_that(funckeys[pos], has_entries(funckey))

    def check_provd_does_not_have_funckey(self, pos):
        config = self.provd.configs.get(self.device['id'])
        funckeys = config['raw_config']['funckeys']

        assert_that(funckeys, is_not(has_key(pos)))

    def add_funckey_to_user(self, pos, funckey):
        response = confd.users(self.user['id']).funckeys(pos).put(**funckey)
        response.assert_ok()


class TestAllFuncKeyDestinations(BaseTestFuncKey):
    def setUp(self):
        super().setUp()

        user_exten = '1000'
        group_exten = '2000'
        queue_exten = '3000'
        conf_exten = '4000'
        forward_number = '5000'
        custom_exten = '9999'
        paging_number = '1234'
        self.parking_exten = '700'
        park_pos = 701

        self.group = confd.groups.post(label='mygroup', tenant_uuid=MAIN_TENANT).item
        self.group_extension = confd.extensions.post(
            exten=group_exten,
            context='default',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.group_extension.associate(self.group['uuid'], self.group_extension['id'])

        self.parking_lot = confd.parkinglots.post(
            slots_start=str(park_pos),
            slots_end=str(park_pos),
            tenant_uuid=MAIN_TENANT,
        ).item
        self.parking_lot_extension = confd.extensions.post(
            exten=self.parking_exten,
            context='default',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.parking_lot_extension.associate(
            self.parking_lot['id'],
            self.parking_lot_extension['id'],
        )

        self.queue = confd.queues.post(name='myqueue', tenant_uuid=MAIN_TENANT).item
        self.queue_extension = confd.extensions.post(
            exten=queue_exten,
            context='default',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.queue_extension.associate(self.queue['id'], self.queue_extension['id'])

        self.conference = confd.conferences.post(tenant_uuid=MAIN_TENANT).item
        self.conference_extension = confd.extensions.post(
            exten=conf_exten,
            context='default',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.conference_extension.associate(
            self.conference['id'],
            self.conference_extension['id'],
        )

        self.agent = confd.agents.post(number='1000', tenant_uuid=MAIN_TENANT).item
        h.user_agent.associate(self.user['id'], self.agent['id'])

        self.paging = confd.pagings.post(
            number=paging_number,
            tenant_uuid=MAIN_TENANT,
        ).item

        self.call_filter = confd.callfilters.post(
            name='mycallfilter',
            strategy='all',
            source='all',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.call_filter_surrogate_user.associate(
            self.call_filter['id'],
            [self.user['uuid']],
        )
        self.call_filter = confd.callfilters(self.call_filter['id']).get().item
        self.filter_member_id = self.call_filter['surrogates']['users'][0]['member_id']

        self.provd_funckeys = {
            '1': {'label': '', 'type': 'speeddial', 'line': 1, 'value': user_exten},
            '2': {'label': '', 'type': 'speeddial', 'line': 1, 'value': group_exten},
            '3': {'label': '', 'type': 'speeddial', 'line': 1, 'value': queue_exten},
            '4': {'label': '', 'type': 'speeddial', 'line': 1, 'value': conf_exten},
            '5': {'label': '', 'type': 'speeddial', 'line': 1, 'value': custom_exten},
            '6': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*10'},
            '7': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*9'},
            '8': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*735{user_id}***226'.format(user_id=self.user['id']),
            },
            '9': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*735{user_id}***227'.format(user_id=self.user['id']),
            },
            '10': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*735{user_id}***225'.format(user_id=self.user['id']),
            },
            '11': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*8'},
            '12': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*34'},
            '13': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*36'},
            '14': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*735{user_id}***290'.format(user_id=self.user['id']),
            },
            '15': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*98'},
            '16': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*92'},
            '17': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*735{user_id}***222'.format(user_id=self.user['id']),
            },
            '18': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*735{user_id}***223'.format(user_id=self.user['id']),
            },
            '19': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*735{user_id}***221'.format(user_id=self.user['id']),
            },
            '20': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*735{user_id}***223*{fwd}'.format(
                    user_id=self.user['id'], fwd=forward_number
                ),
            },
            '21': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*1'},
            '22': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*2'},
            '23': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': f'*735{self.user["id"]}***231***3{self.agent["id"]}',
            },
            '24': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': f'*735{self.user["id"]}***232***3{self.agent["id"]}',
            },
            '25': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': f'*735{self.user["id"]}***230***3{self.agent["id"]}',
            },
            '26': {'label': '', 'type': 'speeddial', 'line': 1, 'value': str(park_pos)},
            '27': {'label': '', 'type': 'park', 'line': 1, 'value': self.parking_exten},
            '28': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*11{paging}'.format(paging=paging_number),
            },
            '29': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': '*37{member_id}'.format(member_id=self.filter_member_id),
            },
            '30': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*3'},
            '31': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*20'},
            '32': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': f'*735{self.user["id"]}***251*{self.group["id"]}',
            },
            '33': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': f'*735{self.user["id"]}***252*{self.group["id"]}',
            },
            '34': {
                'label': '',
                'type': 'speeddial',
                'line': 1,
                'value': f'*735{self.user["id"]}***250*{self.group["id"]}',
            },
        }

        self.confd_funckeys = {
            '1': {
                'blf': False,
                'destination': {'type': 'user', 'user_id': self.user['id']},
            },
            '2': {
                'blf': False,
                'destination': {'type': 'group', 'group_id': self.group['id']},
            },
            '3': {
                'blf': False,
                'destination': {'type': 'queue', 'queue_id': self.queue['id']},
            },
            '4': {
                'blf': False,
                'destination': {
                    'type': 'conference',
                    'conference_id': self.conference['id'],
                },
            },
            '5': {
                'blf': False,
                'destination': {'type': 'custom', 'exten': custom_exten},
            },
            '6': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'phonestatus'},
            },
            '7': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'recsnd'},
            },
            '8': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'callrecord'},
            },
            '9': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'incallfilter'},
            },
            '10': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'enablednd'},
            },
            '11': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'pickup'},
            },
            '12': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'calllistening'},
            },
            '13': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'directoryaccess'},
            },
            '14': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'enablevm'},
            },
            '15': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'vmusermsg'},
            },
            '16': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'vmuserpurge'},
            },
            '17': {
                'blf': False,
                'destination': {'type': 'forward', 'forward': 'noanswer'},
            },
            '18': {'blf': False, 'destination': {'type': 'forward', 'forward': 'busy'}},
            '19': {
                'blf': False,
                'destination': {'type': 'forward', 'forward': 'unconditional'},
            },
            '20': {
                'blf': False,
                'destination': {
                    'type': 'forward',
                    'forward': 'busy',
                    'exten': forward_number,
                },
            },
            '21': {
                'blf': False,
                'destination': {'type': 'transfer', 'transfer': 'blind'},
            },
            '22': {
                'blf': False,
                'destination': {'type': 'transfer', 'transfer': 'attended'},
            },
            '23': {
                'blf': False,
                'destination': {
                    'type': 'agent',
                    'action': 'login',
                    'agent_id': self.agent['id'],
                },
            },
            '24': {
                'blf': False,
                'destination': {
                    'type': 'agent',
                    'action': 'logout',
                    'agent_id': self.agent['id'],
                },
            },
            '25': {
                'blf': False,
                'destination': {
                    'type': 'agent',
                    'action': 'toggle',
                    'agent_id': self.agent['id'],
                },
            },
            '26': {
                'blf': False,
                'destination': {
                    'type': 'park_position',
                    'parking_lot_id': self.parking_lot['id'],
                    'position': park_pos,
                },
            },
            '27': {
                'blf': False,
                'destination': {
                    'type': 'parking',
                    'parking_lot_id': self.parking_lot['id'],
                },
            },
            '28': {
                'blf': False,
                'destination': {'type': 'paging', 'paging_id': self.paging['id']},
            },
            '29': {
                'blf': False,
                'destination': {
                    'type': 'bsfilter',
                    'filter_member_id': self.filter_member_id,
                },
            },
            '30': {'blf': False, 'destination': {'type': 'onlinerec'}},
            '31': {
                'blf': False,
                'destination': {'type': 'service', 'service': 'fwdundoall'},
            },
            '32': {
                'blf': False,
                'destination': {
                    'type': 'groupmember',
                    'action': 'join',
                    'group_id': self.group['id'],
                },
            },
            '33': {
                'blf': False,
                'destination': {
                    'type': 'groupmember',
                    'action': 'leave',
                    'group_id': self.group['id'],
                },
            },
            '34': {
                'blf': False,
                'destination': {
                    'type': 'groupmember',
                    'action': 'toggle',
                    'group_id': self.group['id'],
                },
            },
        }

        self.exclude_for_template = ['23', '24', '25', '29']

    def tearDown(self):
        super().tearDown()
        confd.callfilters(self.call_filter['id']).delete().assert_deleted()
        confd.pagings(self.paging['id']).delete().assert_deleted()
        confd.agents(self.agent['id']).delete().assert_deleted()
        confd.conferences(self.conference['id']).delete().assert_deleted()
        confd.extensions(self.conference_extension['id']).delete().assert_deleted()
        confd.queues(self.queue['id']).delete().assert_deleted()
        confd.extensions(self.queue_extension['id']).delete().assert_deleted()
        confd.parkinglots(self.parking_lot['id']).delete().assert_deleted()
        confd.extensions(self.parking_lot_extension['id']).delete().assert_deleted()
        confd.groups(self.group['id']).delete().assert_deleted()
        confd.extensions(self.group_extension['id']).delete().assert_deleted()

    def test_when_creating_template_then_all_func_keys_created(self):
        for position in self.exclude_for_template:
            del self.confd_funckeys[position]

        response = confd.funckeys.templates.post(
            name='mytemplate', keys=self.confd_funckeys
        )
        funckeys = response.item['keys']

        for pos, expected_funckey in self.confd_funckeys.items():
            self.assert_template_has_funckey(funckeys, pos, expected_funckey)

    def test_when_update_template_funckeys(self):
        for position in self.exclude_for_template:
            del self.confd_funckeys[position]
        template = confd.funckeys.templates.post(name='template', keys={}).item

        response = confd.funckeys.templates(template['id']).put(
            name='edited', keys=self.confd_funckeys
        )
        response.assert_updated()

        response = confd.funckeys.templates(template['id']).get()
        funckeys = response.item['keys']

        for pos, expected_funckey in self.confd_funckeys.items():
            expected_funckey['inherited'] = True
            self.assert_template_has_funckey(funckeys, pos, expected_funckey)

    def test_when_update_user_funckeys(self):
        response = confd.users(self.user['id']).funckeys.put(
            name='user1', keys=self.confd_funckeys
        )
        response.assert_updated()

        response = confd.users(self.user['id']).funckeys.get()
        funckeys = response.item['keys']

        for pos, expected_funckey in self.confd_funckeys.items():
            expected_funckey['inherited'] = False
            self.assert_template_has_funckey(funckeys, pos, expected_funckey)

    def assert_template_has_funckey(self, funckeys, pos, expected):
        expected.setdefault('blf', False)
        expected.setdefault('label', None)
        expected.setdefault('inherited', True)
        expected_destination = expected.pop('destination')

        assert_that(funckeys, has_key(pos))
        funckey = funckeys[pos]

        assert_that(funckey, has_entries(expected))
        assert_that(funckey['destination'], has_entries(expected_destination))

    def test_when_adding_func_keys_to_user_then_func_keys_added_in_provd(self):
        for pos, funckey in self.confd_funckeys.items():
            provd_funckey = self.provd_funckeys[pos]
            self.add_funckey_to_user(pos, funckey)
            self.check_provd_has_funckey(pos, provd_funckey)


class TestTemplateAssociation(BaseTestFuncKey):
    def setUp(self):
        super().setUp()

        self.funckeys = {
            '1': {'destination': {'type': 'custom', 'exten': '9999'}},
            '2': {'destination': {'type': 'transfer', 'transfer': 'blind'}},
        }

        self.provd_funckeys = {
            '1': {'label': '', 'type': 'blf', 'line': 1, 'value': '9999'},
            '2': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*1'},
        }

        response = confd.funckeys.templates.post(keys=self.funckeys)
        self.template = response.item

        self.association_url = confd.users(self.user['id']).funckeys.templates(
            self.template['id']
        )
        self.uuid_url = confd.users(self.user['uuid']).funckeys.templates(
            self.template['id']
        )

    def test_associate_already_associated(self):
        self.association_url.put().assert_ok()
        self.association_url.put().assert_ok()

    def test_given_template_has_func_key_when_associated_then_func_key_added_to_provd(
        self,
    ):
        self.association_url.put().assert_ok()

        for pos, funckey in self.provd_funckeys.items():
            self.check_provd_has_funckey(pos, funckey)

    def test_given_template_has_func_key_when_associated_using_uuid_then_func_key_added_to_provd(
        self,
    ):
        self.uuid_url.put().assert_ok()

        for pos, funckey in self.provd_funckeys.items():
            self.check_provd_has_funckey(pos, funckey)

    def test_when_template_dissociated_then_func_key_removed_from_provd(self):
        self.association_url.put().assert_updated()
        self.association_url.delete().assert_deleted()

        for pos in self.provd_funckeys.keys():
            self.check_provd_does_not_have_funckey(pos)

    def test_when_template_dissociated_using_uuid_then_func_key_removed_from_provd(
        self,
    ):
        self.uuid_url.put().assert_updated()
        self.uuid_url.delete().assert_deleted()

        for pos in self.provd_funckeys.keys():
            self.check_provd_does_not_have_funckey(pos)

    def test_given_user_has_funckey_when_template_associated_then_funckeys_merged(self):
        second_funckey = {'destination': {'type': 'user', 'user_id': self.user['id']}}
        third_funckey = {'destination': {'type': 'service', 'service': 'phonestatus'}}

        first_provd_funckey = self.provd_funckeys['1']
        second_provd_funckey = {'label': '', 'type': 'blf', 'line': 1, 'value': '1000'}
        third_provd_fundkey = {
            'label': '',
            'type': 'speeddial',
            'line': 1,
            'value': '*10',
        }

        with confd.users(self.user['id']).funckeys as url:
            url(2).put(**second_funckey).assert_updated()
            url(3).put(**third_funckey).assert_updated()

        self.association_url.put().assert_updated()

        self.check_provd_has_funckey('1', first_provd_funckey)
        self.check_provd_has_funckey('2', second_provd_funckey)
        self.check_provd_has_funckey('3', third_provd_fundkey)

    def test_given_template_associated_when_deleting_then_removes_funckeys(self):
        self.association_url.put().assert_updated()

        response = confd.funckeys.templates(self.template['id']).delete()
        response.assert_ok()

        for pos in self.provd_funckeys.keys():
            self.check_provd_does_not_have_funckey(pos)

    def test_given_template_associated_when_getting_func_key_then_fetches_from_unified_template(
        self,
    ):
        self.association_url.put().assert_updated()

        response = confd.users(self.user['id']).funckeys(1).get()

        assert_that(
            response.item,
            has_entries(
                inherited=True,
                destination=has_entries(self.funckeys['1']['destination']),
            ),
        )

    def test_given_template_associated_when_getting_func_key_using_uuid_then_fetches_from_unified_template(  # noqa
        self,
    ):
        self.uuid_url.put().assert_updated()

        response = confd.users(self.user['uuid']).funckeys(1).get()

        assert_that(
            response.item,
            has_entries(
                inherited=True,
                destination=has_entries(self.funckeys['1']['destination']),
            ),
        )

    def test_given_template_associated_when_getting_association_then_user_associated(
        self,
    ):
        self.association_url.put().assert_updated()

        response = confd.users(self.user['id']).funckeys.templates.get()

        assert_that(
            response.items,
            contains(
                has_entries(user_id=self.user['id'], template_id=self.template['id'])
            ),
        )

    def test_given_template_associated_when_getting_association_using_uuid_then_user_associated(
        self,
    ):
        self.uuid_url.put().assert_updated()

        response = confd.users(self.user['uuid']).funckeys.templates.get()

        assert_that(
            response.items,
            contains(
                has_entries(user_id=self.user['id'], template_id=self.template['id'])
            ),
        )

    def test_given_template_associated_when_getting_association_then_template_associated(
        self,
    ):
        self.association_url.put().assert_updated()

        response = confd.funckeys.templates(self.template['id']).users.get()

        assert_that(
            response.items,
            contains(
                has_entries(user_id=self.user['id'], template_id=self.template['id'])
            ),
        )

    def test_associate_errors(self):
        fake_user = confd.users(FAKE_ID).funckeys.templates(self.template['id']).put
        fake_template = confd.users(self.user['id']).funckeys.templates(FAKE_ID).put

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_template, 'FuncKeyTemplate')

    def test_dissociate_errors(self):
        fake_user = confd.users(FAKE_ID).funckeys.templates(self.template['id']).delete
        fake_template = confd.users(self.user['id']).funckeys.templates(FAKE_ID).delete

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_template, 'FuncKeyTemplate')

    def test_get_errors(self):
        fake_user = confd.users(FAKE_ID).funckeys.templates.get
        s.check_resource_not_found(fake_user, 'User')

        # XXX: This is a bug that do not raise an error
        # fake_template = confd.funckeys.templates(FAKE_ID).users.get
        # s.check_resource_not_found(fake_template, 'FuncKeyTemplate')

    def test_associate_second_template_then_overwrite_previous_template(self):
        funckeys_2 = {
            '1': {'destination': {'type': 'user', 'user_id': self.user['id']}},
            '2': {'destination': {'type': 'onlinerec'}},
        }
        provd_funckeys_2 = {
            '1': {'label': '', 'type': 'blf', 'line': 1, 'value': '1000'},
            '2': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*3'},
        }
        template_2 = confd.funckeys.templates.post(keys=funckeys_2).item

        confd.users(self.user['id']).funckeys.templates(
            self.template['id']
        ).put().assert_updated()
        self.check_provd_has_funckey('1', self.provd_funckeys['1'])
        self.check_provd_has_funckey('2', self.provd_funckeys['2'])

        confd.users(self.user['id']).funckeys.templates(
            template_2['id']
        ).put().assert_updated()
        self.check_provd_has_funckey('1', provd_funckeys_2['1'])
        self.check_provd_has_funckey('2', provd_funckeys_2['2'])

    def test_get_template_after_dissociation(self):
        self.association_url.put().assert_updated()
        self.association_url.delete().assert_deleted()

        response = confd.users(self.user['id']).funckeys.templates.get()
        assert_that(response.items, empty())

        response = confd.users(self.user['uuid']).funckeys.templates.get()
        assert_that(response.items, empty())


@fixtures.user()
@fixtures.funckey_template()
def test_dissociate_not_associated(user, funckey_template):
    response = (
        confd.users(user['id']).funckeys.templates(funckey_template['id']).delete()
    )
    response.assert_deleted()


@fixtures.user()
@fixtures.funckey_template()
def test_delete_funckey_template_when_user_and_funckey_template_associated(
    user, funckey_template
):
    with a.user_funckey_template(user, funckey_template, check=False):
        response = confd.users(user['id']).funckeys.templates.get()
        assert_that(response.items, not_(empty()))
        confd.funckeys.templates(funckey_template['id']).delete().assert_deleted()
        response = confd.users(user['id']).funckeys.templates.get()
        assert_that(response.items, empty())


@fixtures.user()
@fixtures.funckey_template()
def test_delete_user_when_user_and_funckey_template_associated(user, funckey_template):
    with a.user_funckey_template(user, funckey_template, check=False):
        response = confd.funckeys.templates(funckey_template['id']).users.get()
        assert_that(response.items, not_(empty()))
        confd.users(user['id']).delete().assert_deleted()
        response = confd.funckeys.templates(funckey_template['id']).users.get()
        assert_that(response.items, empty())


@fixtures.user()
def test_get_user_destination_relation(user):
    destination = {'type': 'user', 'user_id': user['id']}
    response = confd.users(user['id']).funckeys(1).put(destination=destination)
    response.assert_updated()

    response = confd.users(user['id']).funckeys(1).get()
    assert_that(
        response.item,
        has_entries(
            destination=has_entries(
                user_id=user['id'],
                user_firstname=user['firstname'],
                user_lastname=user['lastname'],
            )
        ),
    )


@fixtures.call_filter()
@fixtures.user()
def test_get_bsfilter_destination_relation(call_filter, user):
    with a.call_filter_surrogate_user(call_filter, user):
        user_member = (
            confd.callfilters(call_filter['id']).get().item['surrogates']['users'][0]
        )
        destination = {'type': 'bsfilter', 'filter_member_id': user_member['member_id']}
        response = confd.users(user['id']).funckeys(1).put(destination=destination)
        response.assert_updated()

        response = confd.users(user['id']).funckeys(1).get()
        assert_that(
            response.item,
            has_entries(
                destination=has_entries(
                    filter_member_id=user_member['member_id'],
                    filter_member_firstname=user['firstname'],
                    filter_member_lastname=user['lastname'],
                )
            ),
        )


@fixtures.user()
@fixtures.group()
def test_get_group_destination_relation(user, group):
    destination = {'type': 'group', 'group_id': group['id']}
    response = confd.users(user['id']).funckeys(1).put(destination=destination)
    response.assert_updated()

    response = confd.users(user['id']).funckeys(1).get()
    assert_that(
        response.item,
        has_entries(
            destination=has_entries(group_id=group['id'], group_name=group['name'])
        ),
    )


@fixtures.user()
@fixtures.parking_lot(slots_start='801', slots_end='850')
def test_get_park_position_destination_relation(user, parking_lot):
    destination = {
        'type': 'park_position',
        'parking_lot_id': parking_lot['id'],
        'position': 801,
    }
    response = confd.users(user['id']).funckeys(1).put(destination=destination)
    response.assert_updated()

    response = confd.users(user['id']).funckeys(1).get()
    assert_that(
        response.item,
        has_entries(
            destination=has_entries(
                parking_lot_id=parking_lot['id'],
                parking_lot_name=parking_lot['name'],
            )
        ),
    )


@fixtures.user()
@fixtures.parking_lot()
@fixtures.extension()
def test_get_parking_destination_relation(user, parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension):
        destination = {
            'type': 'parking',
            'parking_lot_id': parking_lot['id'],
        }
        response = confd.users(user['id']).funckeys(1).put(destination=destination)
        response.assert_updated()

        response = confd.users(user['id']).funckeys(1).get()
        assert_that(
            response.item,
            has_entries(
                destination=has_entries(
                    parking_lot_id=parking_lot['id'],
                    parking_lot_name=parking_lot['name'],
                )
            ),
        )


@fixtures.user()
@fixtures.parking_lot(slots_start='801', slots_end='850')
def test_create_park_position_wrong_position(user, parking_lot):
    destination = {
        'type': 'park_position',
        'parking_lot_id': parking_lot['id'],
        'position': 900,
    }
    response = confd.users(user['id']).funckeys(1).put(destination=destination)
    response.assert_match(400, e.outside_range())


@fixtures.user()
@fixtures.parking_lot()
def test_create_parking_without_extension(user, parking_lot):
    destination = {
        'type': 'parking',
        'parking_lot_id': parking_lot['id'],
    }
    response = confd.users(user['id']).funckeys(1).put(destination=destination)
    response.assert_match(400, e.missing_association())


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_get_user_funckeys_multi_tenant(main, sub):
    response = confd.users(main['uuid']).funckeys.get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['uuid']).funckeys.get(wazo_tenant=MAIN_TENANT)
    response.assert_ok()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_edit_user_funckeys_multi_tenant(main, sub):
    response = confd.users(main['uuid']).funckeys.put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['uuid']).funckeys.put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_get_user_funckeys_position_multi_tenant(main, sub):
    body = {'destination': {'type': 'custom', 'exten': '123'}}
    confd.users(main['uuid']).funckeys(1).put(body).assert_updated()
    confd.users(sub['uuid']).funckeys(1).put(body).assert_updated()

    response = confd.users(main['uuid']).funckeys(1).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['uuid']).funckeys(1).get(wazo_tenant=MAIN_TENANT)
    response.assert_ok()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_edit_user_funckeys_position_multi_tenant(main, sub):
    body = {'destination': {'type': 'custom', 'exten': '123'}}
    confd.users(main['uuid']).funckeys(1).put(body).assert_updated()
    confd.users(sub['uuid']).funckeys(1).put(body).assert_updated()

    response = confd.users(main['uuid']).funckeys(1).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['uuid']).funckeys(1).put(wazo_tenant=MAIN_TENANT, **body)
    response.assert_updated()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_delete_user_funckeys_position_multi_tenant(main, sub):
    body = {'destination': {'type': 'custom', 'exten': '123'}}
    confd.users(main['uuid']).funckeys(1).put(body).assert_updated()
    confd.users(sub['uuid']).funckeys(1).put(body).assert_updated()

    response = confd.users(main['uuid']).funckeys(1).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['uuid']).funckeys(1).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.funckey_template(wazo_tenant=MAIN_TENANT)
@fixtures.funckey_template(wazo_tenant=SUB_TENANT)
def test_get_template_users_multi_tenant(main, sub):
    response = confd.funckeys.templates(main['id']).users.get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='FuncKeyTemplate'))

    response = confd.funckeys.templates(sub['id']).users.get(wazo_tenant=MAIN_TENANT)
    response.assert_ok()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_get_user_templates_multi_tenant(main, sub):
    response = confd.users(main['uuid']).funckeys.templates.get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['uuid']).funckeys.templates.get(wazo_tenant=MAIN_TENANT)
    response.assert_ok()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.funckey_template(wazo_tenant=MAIN_TENANT)
@fixtures.funckey_template(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_user, sub_user, main_template, sub_template):
    response = (
        confd.users(main_user['uuid'])
        .funckeys.templates(sub_template['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('User'))

    response = (
        confd.users(sub_user['uuid'])
        .funckeys.templates(main_template['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('FuncKeyTemplate'))

    response = (
        confd.users(main_user['uuid'])
        .funckeys.templates(sub_template['id'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.funckey_template(wazo_tenant=MAIN_TENANT)
@fixtures.funckey_template(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_user, sub_user, main_template, sub_template):
    response = (
        confd.users(main_user['uuid'])
        .funckeys.templates(sub_template['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('User'))

    response = (
        confd.users(sub_user['uuid'])
        .funckeys.templates(main_template['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('FuncKeyTemplate'))


@fixtures.context(label='sub-tenant', wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.funckey_template(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.funckey_template(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
@fixtures.conference(wazo_tenant=SUB_TENANT)
@fixtures.agent(wazo_tenant=SUB_TENANT)
@fixtures.paging(wazo_tenant=SUB_TENANT)
@fixtures.call_filter(wazo_tenant=SUB_TENANT)
@fixtures.parking_lot(wazo_tenant=SUB_TENANT)
def test_func_key_destinations_multi_tenant(
    context,
    main_user,
    main_template,
    sub_user,
    sub_template,
    user,
    group,
    queue,
    conference,
    agent,
    paging,
    call_filter,
    parking,
):
    confd.callfilters(call_filter['id']).surrogates.users.put(users=[sub_user])
    response = confd.callfilters(call_filter['id']).get()
    filter_member_id = response.item['surrogates']['users'][0]['member_id']

    parking_extension = helpers.extension.generate_extension(
        context=context['name'],
        wazo_tenant=SUB_TENANT,
    )
    response = (
        confd.parkinglots(parking['id']).extensions(parking_extension['id']).put()
    )
    response.assert_updated()

    funckeys = {
        '1': {'type': 'user', 'user_id': user['id']},
        '2': {'type': 'group', 'group_id': group['id']},
        '3': {'type': 'queue', 'queue_id': queue['id']},
        '4': {'type': 'conference', 'conference_id': conference['id']},
        '6': {'type': 'agent', 'action': 'login', 'agent_id': agent['id']},
        '7': {'type': 'agent', 'action': 'logout', 'agent_id': agent['id']},
        '8': {'type': 'agent', 'action': 'toggle', 'agent_id': agent['id']},
        '9': {
            'type': 'park_position',
            'parking_lot_id': parking['id'],
            'position': parking['slots_start'],
        },
        '10': {'type': 'paging', 'paging_id': paging['id']},
        '11': {'type': 'bsfilter', 'filter_member_id': filter_member_id},
        '12': {'type': 'groupmember', 'action': 'join', 'group_id': group['id']},
        '13': {'type': 'groupmember', 'action': 'leave', 'group_id': group['id']},
        '14': {'type': 'groupmember', 'action': 'toggle', 'group_id': group['id']},
        '15': {'type': 'parking', 'parking_lot_id': parking['id']},
    }
    exclude_for_template = ['6', '7', '8', '11']

    for position, destination in funckeys.items():
        template_args = {'keys': {position: {'destination': destination}}}
        fk_args = template_args['keys'][position]

        response = confd.users(main_user['uuid']).funckeys(position).put(fk_args)
        response.assert_status(400)

        response = confd.users(sub_user['uuid']).funckeys(position).put(fk_args)
        response.assert_updated()

        response = confd.users(main_user['uuid']).funckeys.put(template_args)
        response.assert_status(400)

        response = confd.users(sub_user['uuid']).funckeys.put(template_args)
        response.assert_updated()

        if position not in exclude_for_template:
            response = confd.funckeys.templates(main_template['id'])(position).put(
                fk_args
            )
            response.assert_status(400)

            response = confd.funckeys.templates(sub_template['id'])(position).put(
                fk_args
            )
            response.assert_updated()

            response = confd.funckeys.templates.post(template_args)
            response.assert_status(400)

            response = confd.funckeys.templates(main_template['id']).put(template_args)
            response.assert_status(400)

            response = confd.funckeys.templates(sub_template['id']).put(template_args)
            response.assert_updated()

            response = confd.funckeys.templates.post(
                template_args, wazo_tenant=SUB_TENANT
            )
            response.assert_created()

            response = confd.funckeys.templates(response.item['id']).delete()
            response.assert_deleted()

    helpers.extension.delete_extension(parking_extension['id'])


class TestBlfFuncKeys(BaseTestFuncKey):
    def setUp(self):
        super().setUp()

        user_exten = '1000'
        group_exten = '2000'
        conf_exten = '4000'
        forward_number = '5000'
        custom_exten = '9999'
        self.parking_exten = '700'
        park_pos = 701

        self.group = confd.groups.post(label='mygroup', tenant_uuid=MAIN_TENANT).item
        self.group_extension = confd.extensions.post(
            exten=group_exten,
            context='default',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.group_extension.associate(self.group['uuid'], self.group_extension['id'])

        self.parking_lot = confd.parkinglots.post(
            slots_start=str(park_pos),
            slots_end=str(park_pos),
            tenant_uuid=MAIN_TENANT,
        ).item
        self.parking_lot_extension = confd.extensions.post(
            exten=self.parking_exten,
            context='default',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.parking_lot_extension.associate(
            self.parking_lot['id'],
            self.parking_lot_extension['id'],
        )

        self.conference = confd.conferences.post(tenant_uuid=MAIN_TENANT).item
        self.conference_extension = confd.extensions.post(
            exten=conf_exten,
            context='default',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.conference_extension.associate(
            self.conference['id'],
            self.conference_extension['id'],
        )

        self.agent = confd.agents.post(number='1000', tenant_uuid=MAIN_TENANT).item
        h.user_agent.associate(self.user['id'], self.agent['id'])

        self.call_filter = confd.callfilters.post(
            name='mycallfilter',
            strategy='all',
            source='all',
            tenant_uuid=MAIN_TENANT,
        ).item
        h.call_filter_surrogate_user.associate(
            self.call_filter['id'],
            [self.user['uuid']],
        )
        self.call_filter = confd.callfilters(self.call_filter['id']).get().item
        self.filter_member_id = self.call_filter['surrogates']['users'][0]['member_id']

        self.confd_funckeys = {
            '1': {'destination': {'type': 'user', 'user_id': self.user['id']}},
            '4': {
                'destination': {
                    'type': 'conference',
                    'conference_id': self.conference['id'],
                }
            },
            '5': {'destination': {'type': 'custom', 'exten': custom_exten}},
            '8': {'destination': {'type': 'service', 'service': 'callrecord'}},
            '9': {'destination': {'type': 'service', 'service': 'incallfilter'}},
            '10': {'destination': {'type': 'service', 'service': 'enablednd'}},
            '14': {'destination': {'type': 'service', 'service': 'enablevm'}},
            '17': {'destination': {'type': 'forward', 'forward': 'noanswer'}},
            '18': {'destination': {'type': 'forward', 'forward': 'busy'}},
            '19': {'destination': {'type': 'forward', 'forward': 'unconditional'}},
            '20': {
                'destination': {
                    'type': 'forward',
                    'forward': 'busy',
                    'exten': forward_number,
                }
            },
            '23': {
                'destination': {
                    'type': 'agent',
                    'action': 'login',
                    'agent_id': self.agent['id'],
                }
            },
            '24': {
                'destination': {
                    'type': 'agent',
                    'action': 'logout',
                    'agent_id': self.agent['id'],
                }
            },
            '25': {
                'destination': {
                    'type': 'agent',
                    'action': 'toggle',
                    'agent_id': self.agent['id'],
                }
            },
            '26': {
                'destination': {
                    'type': 'park_position',
                    'parking_lot_id': self.parking_lot['id'],
                    'position': park_pos,
                }
            },
            '29': {
                'destination': {
                    'type': 'bsfilter',
                    'filter_member_id': self.filter_member_id,
                }
            },
            '32': {
                'destination': {
                    'type': 'groupmember',
                    'action': 'join',
                    'group_id': self.group['id'],
                }
            },
            '33': {
                'destination': {
                    'type': 'groupmember',
                    'action': 'leave',
                    'group_id': self.group['id'],
                }
            },
            '34': {
                'destination': {
                    'type': 'groupmember',
                    'action': 'toggle',
                    'group_id': self.group['id'],
                }
            },
        }

        self.provd_funckeys = {
            '1': {'label': '', 'type': 'blf', 'line': 1, 'value': user_exten},
            '4': {'label': '', 'type': 'blf', 'line': 1, 'value': conf_exten},
            '5': {'label': '', 'type': 'blf', 'line': 1, 'value': custom_exten},
            '8': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***226',
            },
            '9': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***227',
            },
            '10': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***225',
            },
            '14': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***290',
            },
            '17': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***222',
            },
            '18': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***223',
            },
            '19': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***221',
            },
            '20': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***223*{forward_number}',
            },
            '23': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***231***3{self.agent["id"]}',
            },
            '24': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***232***3{self.agent["id"]}',
            },
            '25': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***230***3{self.agent["id"]}',
            },
            '26': {'label': '', 'type': 'blf', 'line': 1, 'value': str(park_pos)},
            '29': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*37{self.filter_member_id}',
            },
            '32': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***251*{self.group["id"]}',
            },
            '33': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***252*{self.group["id"]}',
            },
            '34': {
                'label': '',
                'type': 'blf',
                'line': 1,
                'value': f'*735{self.user["id"]}***250*{self.group["id"]}',
            },
        }

    def tearDown(self):
        super().tearDown()
        confd.callfilters(self.call_filter['id']).delete().assert_deleted()
        confd.agents(self.agent['id']).delete().assert_deleted()
        confd.conferences(self.conference['id']).delete().assert_deleted()
        confd.extensions(self.conference_extension['id']).delete().assert_deleted()
        confd.parkinglots(self.parking_lot['id']).delete().assert_deleted()
        confd.extensions(self.parking_lot_extension['id']).delete().assert_deleted()
        confd.groups(self.group['id']).delete().assert_deleted()
        confd.extensions(self.group_extension['id']).delete().assert_deleted()

    def test_when_creating_funckey_then_blf_activated_by_default(self):
        funckey = {'destination': {'type': 'custom', 'exten': '9999'}}
        response = confd.funckeys.templates.post(keys={'1': funckey})

        created_funckey = response.item['keys']['1']
        assert_that(created_funckey, has_entry('blf', True))

    def test_when_adding_blf_func_keys_to_user_then_func_keys_added_in_provd(self):
        for pos, funckey in self.confd_funckeys.items():
            provd_funckey = self.provd_funckeys[pos]
            self.add_funckey_to_user(pos, funckey)
            self.check_provd_has_funckey(pos, provd_funckey)

    def test_when_creating_func_key_that_cannot_be_blf_then_func_key_isnt_blf_in_provd(
        self,
    ):
        position = '1'
        funckey = {
            'blf': True,
            'destination': {'type': 'transfer', 'transfer': 'blind'},
        }
        provd_funckey = {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*1'}

        self.add_funckey_to_user(position, funckey)
        self.check_provd_has_funckey(position, provd_funckey)
