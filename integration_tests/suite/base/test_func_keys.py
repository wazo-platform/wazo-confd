# -*- coding: utf-8 -*-

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

import unittest
from hamcrest import (assert_that,
                      contains,
                      empty,
                      has_entries,
                      has_entry,
                      has_key,
                      is_not,
                      not_)

from test_api import confd
from test_api import helpers
from test_api import db
from test_api import provd
from test_api import associations as a
from test_api import scenarios as s
from test_api import fixtures

FAKE_ID = 999999999


class BaseTestFuncKey(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.provd = provd
        self.provd.reset()

        self.db.recreate()

        self.user = helpers.user.generate_user()
        self.device = self.setup_device(self.user['id'], '1000')

    def setup_device(self, user_id, exten):
        line = helpers.line_sip.generate_line()
        extension = helpers.extension.add_extension(exten=exten,
                                                    context='default')
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


class TestUserWithFuncKey(BaseTestFuncKey):

    def setUp(self):
        super(TestUserWithFuncKey, self).setUp()

        self.destination = {'type': 'custom', 'exten': '1234'}
        self.pos = '1'

        self.funckey_url = confd.users(self.user['id']).funckeys(self.pos)
        self.uuid_url = confd.users(self.user['uuid']).funckeys(self.pos)

        self.funckey_url.put(destination=self.destination).assert_ok()

    def test_when_line_has_another_position_then_func_key_generated(self):
        user = helpers.user.generate_user()
        sip = helpers.endpoint_sip.generate_sip()
        line = helpers.line.generate_line(position=2)
        extension = helpers.extension.generate_extension()
        device = helpers.device.generate_device()

        helpers.line_endpoint_sip.associate(line['id'], sip['id'])
        helpers.line_extension.associate(line['id'], extension['id'])
        helpers.user_line.associate(user['id'], line['id'])
        helpers.line_device.associate(line['id'], device['id'])

        url = confd.users(user['id']).funckeys(self.pos)
        url.put(destination=self.destination).assert_ok()

        expected_funckey = {'label': None,
                            'inherited': False,
                            'blf': True}
        expected_destination = {'type': self.destination['type'],
                                'exten': self.destination['exten'],
                                'href': None}

        response = url.get()
        assert_that(response.item, has_entries(expected_funckey))
        assert_that(response.item['destination'], has_entries(expected_destination))

    def test_when_getting_position_then_func_key_returned(self):
        expected_funckey = {'label': None,
                            'inherited': False,
                            'blf': True}
        expected_destination = {'type': self.destination['type'],
                                'exten': self.destination['exten'],
                                'href': None}

        response = self.funckey_url.get()

        assert_that(response.item, has_entries(expected_funckey))
        assert_that(response.item['destination'], has_entries(expected_destination))

        response = self.uuid_url.get()

        assert_that(response.item, has_entries(expected_funckey))
        assert_that(response.item['destination'], has_entries(expected_destination))

    def test_when_updating_position_then_func_key_modified_in_provd(self):
        modified_funckey = {'blf': False,
                            'label': 'myfunckey',
                            'destination': {'type': 'park_position',
                                            'position': 701}}
        uuid_funckey = {'blf': False,
                        'label': 'myfunckey',
                        'destination': {'type': 'park_position',
                                        'position': 702}}

        provd_funckey = {'label': 'myfunckey',
                         'type': 'speeddial',
                         'line': 1,
                         'value': '701'}
        provd_uuid_funckey = {'label': 'myfunckey',
                              'type': 'speeddial',
                              'line': 1,
                              'value': '702'}

        self.funckey_url.put(**modified_funckey).assert_updated()
        self.check_provd_has_funckey(self.pos, provd_funckey)

        self.uuid_url.put(**uuid_funckey).assert_updated()
        self.check_provd_has_funckey(self.pos, provd_uuid_funckey)

    def test_when_deleting_position_then_func_key_removed(self):
        response = self.funckey_url.delete()
        response.assert_ok()

        response = self.funckey_url.get()
        response.assert_status(404)

        self.check_provd_does_not_have_funckey(self.pos)

    def test_when_deleting_position_using_uuid_then_func_key_removed(self):
        response = self.uuid_url.delete()
        response.assert_ok()

        response = self.funckey_url.get()
        response.assert_status(404)

        self.check_provd_does_not_have_funckey(self.pos)

    def test_get_user_funckeys(self):
        destination_2 = {'type': 'custom', 'exten': '456'}
        destination_3 = {'type': 'custom', 'exten': '789'}
        confd.users(self.user['id']).funckeys(2).put(destination=destination_2)
        confd.users(self.user['id']).funckeys(3).put(destination=destination_3)

        response = confd.users(self.user['id']).funckeys.get()

        expected_result = has_entries({'keys': has_entries({
            '1': has_entries({'destination': has_entries(self.destination)}),
            '2': has_entries({'destination': has_entries(destination_2)}),
            '3': has_entries({'destination': has_entries(destination_3)})})
        })

        assert_that(response.item, expected_result)

    def test_put_errors(self):
        fake_user = confd.users(FAKE_ID).funckeys(1).put
        s.check_resource_not_found(fake_user, 'User')

    def test_delete_errors(self):
        fake_user = confd.users(FAKE_ID).funckeys(1).delete
        s.check_resource_not_found(fake_user, 'User')

        # This should raise an error
        # fake_funckey = confd.users(self.user['id']).funckeys(FAKE_ID).delete
        # s.check_resource_not_found(fake_funckey, 'FuncKey')

    def test_get_errors(self):
        fake_user = confd.users(FAKE_ID).funckeys.get
        fake_user_2 = confd.users(FAKE_ID).funckeys(1).get
        fake_funckey = confd.users(self.user['uuid']).funckeys(FAKE_ID).get

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_user_2, 'User')
        s.check_resource_not_found(fake_funckey, 'FuncKey')


class TestAllFuncKeyDestinations(BaseTestFuncKey):

    def setUp(self):
        super(TestAllFuncKeyDestinations, self).setUp()

        user_exten = '1000'
        group_exten = '2000'
        queue_exten = '3000'
        conf_exten = '4000'
        forward_number = '5000'
        custom_exten = '9999'
        paging_number = '1234'
        parking = '700'
        park_pos = 701

        with self.db.queries() as queries:
            group_id = queries.insert_group(number=group_exten)
            queue_id = queries.insert_queue(number=queue_exten)
            conference_id = queries.insert_conference(number=conf_exten)
            agent_id = queries.insert_agent(self.user['id'])
            paging_id = queries.insert_paging(number=paging_number)
            callfilter_id = queries.insert_callfilter()
            filter_member_id = queries.insert_filter_member(callfilter_id,
                                                            self.user['id'])

        self.provd_funckeys = {
            '1': {'label': '', 'type': 'speeddial', 'line': 1, 'value': user_exten},
            '2': {'label': '', 'type': 'speeddial', 'line': 1, 'value': group_exten},
            '3': {'label': '', 'type': 'speeddial', 'line': 1, 'value': queue_exten},
            '4': {'label': '', 'type': 'speeddial', 'line': 1, 'value': conf_exten},
            '5': {'label': '', 'type': 'speeddial', 'line': 1, 'value': custom_exten},
            '6': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*10'},
            '7': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*9'},
            '8': {'label': '', 'type': 'speeddial', 'line': 1,
                  'value': '*735{user_id}***226'.format(user_id=self.user['id'])},
            '9': {'label': '', 'type': 'speeddial', 'line': 1,
                  'value': '*735{user_id}***227'.format(user_id=self.user['id'])},
            '10': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***225'.format(user_id=self.user['id'])},
            '11': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*8'},
            '12': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*34'},
            '13': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*36'},
            '14': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***290'.format(user_id=self.user['id'])},
            '15': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*98'},
            '16': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*92'},
            '17': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***222'.format(user_id=self.user['id'])},
            '18': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***223'.format(user_id=self.user['id'])},
            '19': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***221'.format(user_id=self.user['id'])},
            '20': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***223*{fwd}'.format(user_id=self.user['id'], fwd=forward_number)},
            '21': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*1'},
            '22': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*2'},
            '23': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***231***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '24': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***232***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '25': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*735{user_id}***230***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '26': {'label': '', 'type': 'speeddial', 'line': 1, 'value': str(park_pos)},
            '27': {'label': '', 'type': 'park', 'line': 1, 'value': parking},
            '28': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*11{paging}'.format(paging=paging_number)},
            '29': {'label': '', 'type': 'speeddial', 'line': 1,
                   'value': '*37{member_id}'.format(member_id=filter_member_id)},
            '30': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*3'},
            '31': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*20'},
        }

        self.confd_funckeys = {
            '1': {'blf': False, 'destination': {'type': 'user', 'user_id': self.user['id']}},
            '2': {'blf': False, 'destination': {'type': 'group', 'group_id': group_id}},
            '3': {'blf': False, 'destination': {'type': 'queue', 'queue_id': queue_id}},
            '4': {'blf': False, 'destination': {'type': 'conference', 'conference_id': conference_id}},
            '5': {'blf': False, 'destination': {'type': 'custom', 'exten': custom_exten}},
            '6': {'blf': False, 'destination': {'type': 'service', 'service': 'phonestatus'}},
            '7': {'blf': False, 'destination': {'type': 'service', 'service': 'recsnd'}},
            '8': {'blf': False, 'destination': {'type': 'service', 'service': 'callrecord'}},
            '9': {'blf': False, 'destination': {'type': 'service', 'service': 'incallfilter'}},
            '10': {'blf': False, 'destination': {'type': 'service', 'service': 'enablednd'}},
            '11': {'blf': False, 'destination': {'type': 'service', 'service': 'pickup'}},
            '12': {'blf': False, 'destination': {'type': 'service', 'service': 'calllistening'}},
            '13': {'blf': False, 'destination': {'type': 'service', 'service': 'directoryaccess'}},
            '14': {'blf': False, 'destination': {'type': 'service', 'service': 'enablevm'}},
            '15': {'blf': False, 'destination': {'type': 'service', 'service': 'vmusermsg'}},
            '16': {'blf': False, 'destination': {'type': 'service', 'service': 'vmuserpurge'}},
            '17': {'blf': False, 'destination': {'type': 'forward', 'forward': 'noanswer'}},
            '18': {'blf': False, 'destination': {'type': 'forward', 'forward': 'busy'}},
            '19': {'blf': False, 'destination': {'type': 'forward', 'forward': 'unconditional'}},
            '20': {'blf': False, 'destination': {'type': 'forward', 'forward': 'busy', 'exten': forward_number}},
            '21': {'blf': False, 'destination': {'type': 'transfer', 'transfer': 'blind'}},
            '22': {'blf': False, 'destination': {'type': 'transfer', 'transfer': 'attended'}},
            '23': {'blf': False, 'destination': {'type': 'agent', 'action': 'login', 'agent_id': agent_id}},
            '24': {'blf': False, 'destination': {'type': 'agent', 'action': 'logout', 'agent_id': agent_id}},
            '25': {'blf': False, 'destination': {'type': 'agent', 'action': 'toggle', 'agent_id': agent_id}},
            '26': {'blf': False, 'destination': {'type': 'park_position', 'position': park_pos}},
            '27': {'blf': False, 'destination': {'type': 'parking'}},
            '28': {'blf': False, 'destination': {'type': 'paging', 'paging_id': paging_id}},
            '29': {'blf': False, 'destination': {'type': 'bsfilter', 'filter_member_id': filter_member_id}},
            '30': {'blf': False, 'destination': {'type': 'onlinerec'}},
            '31': {'blf': False, 'destination': {'type': 'service', 'service': 'fwdundoall'}},
        }

        self.exclude_for_template = ['23', '24', '25', '29']

    def test_when_creating_template_then_all_func_keys_created(self):
        for position in self.exclude_for_template:
            del self.confd_funckeys[position]

        response = confd.funckeys.templates.post(name='mytemplate', keys=self.confd_funckeys)
        funckeys = response.item['keys']

        for pos, expected_funckey in self.confd_funckeys.items():
            self.assert_template_has_funckey(funckeys, pos, expected_funckey)

    def test_when_creating_agent_or_bsfilter_for_public_template_then_returns_error(self):
        for position in self.exclude_for_template:
            funckey = self.confd_funckeys[position]
            response = confd.funckeys.templates.post(keys={'1': funckey})
            response.assert_status(400)

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
        super(TestTemplateAssociation, self).setUp()

        self.funckeys = {'1': {'destination': {'type': 'custom', 'exten': '9999'}},
                         '2': {'destination': {'type': 'parking'}}}

        self.provd_funckeys = {
            '1': {'label': '', 'type': 'blf', 'line': 1, 'value': '9999'},
            '2': {'label': '', 'type': 'park', 'line': 1, 'value': '700'}
        }

        response = confd.funckeys.templates.post(keys=self.funckeys)
        self.template = response.item

        self.association_url = confd.users(self.user['id']).funckeys.templates(self.template['id'])
        self.uuid_url = confd.users(self.user['uuid']).funckeys.templates(self.template['id'])

    def test_given_template_has_func_key_when_associated_then_func_key_added_to_provd(self):
        self.association_url.put().assert_ok()

        for pos, funckey in self.provd_funckeys.items():
            self.check_provd_has_funckey(pos, funckey)

    def test_given_template_has_func_key_when_associated_using_uuid_then_func_key_added_to_provd(self):
        self.uuid_url.put().assert_ok()

        for pos, funckey in self.provd_funckeys.items():
            self.check_provd_has_funckey(pos, funckey)

    def test_when_template_dissociated_then_func_key_removed_from_provd(self):
        self.association_url.put().assert_updated()
        self.association_url.delete().assert_deleted()

        for pos in self.provd_funckeys.keys():
            self.check_provd_does_not_have_funckey(pos)

    def test_when_template_dissociated_using_uuid_then_func_key_removed_from_provd(self):
        self.uuid_url.put().assert_updated()
        self.uuid_url.delete().assert_deleted()

        for pos in self.provd_funckeys.keys():
            self.check_provd_does_not_have_funckey(pos)

    def test_given_user_has_funckey_when_template_associated_then_funckeys_merged(self):
        second_funckey = {'destination': {'type': 'user', 'user_id': self.user['id']}}
        third_funckey = {'destination': {'type': 'service', 'service': 'phonestatus'}}

        first_provd_funckey = self.provd_funckeys['1']
        second_provd_funckey = {'label': '', 'type': 'blf', 'line': 1, 'value': '1000'}
        third_provd_fundkey = {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*10'}

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

    def test_given_template_associated_when_getting_func_key_then_fetches_from_unified_template(self):
        self.association_url.put().assert_updated()

        response = confd.users(self.user['id']).funckeys(1).get()

        expected_destination = self.funckeys['1']['destination']
        assert_that(response.item, has_entry('inherited', True))
        assert_that(response.item['destination'], has_entries(expected_destination))

    def test_given_template_associated_when_getting_func_key_using_uuid_then_fetches_from_unified_template(self):
        self.uuid_url.put().assert_updated()

        response = confd.users(self.user['uuid']).funckeys(1).get()

        expected_destination = self.funckeys['1']['destination']
        assert_that(response.item, has_entry('inherited', True))
        assert_that(response.item['destination'], has_entries(expected_destination))

    def test_given_template_associated_when_getting_association_then_user_associated(self):
        self.association_url.put().assert_updated()

        response = confd.users(self.user['id']).funckeys.templates.get()

        expected_association = {'user_id': self.user['id'],
                                'template_id': self.template['id']}

        assert_that(response.items, contains(has_entries(expected_association)))

    def test_given_template_associated_when_getting_association_using_uuid_then_user_associated(self):
        self.uuid_url.put().assert_updated()

        response = confd.users(self.user['uuid']).funckeys.templates.get()

        expected_association = {'user_id': self.user['id'],
                                'template_id': self.template['id']}

        assert_that(response.items, contains(has_entries(expected_association)))

    def test_given_template_associated_when_getting_association_then_template_associated(self):
        self.association_url.put().assert_updated()

        response = confd.funckeys.templates(self.template['id']).users.get()

        expected_association = {'user_id': self.user['id'],
                                'template_id': self.template['id']}

        assert_that(response.items, contains(has_entries(expected_association)))

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
        funckeys_2 = {'1': {'destination': {'type': 'user', 'user_id': self.user['id']}},
                      '2': {'destination': {'type': 'onlinerec'}}}
        provd_funckeys_2 = {
            '1': {'label': '', 'type': 'blf', 'line': 1, 'value': '1000'},
            '2': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*3'},
        }
        template_2 = confd.funckeys.templates.post(keys=funckeys_2).item

        confd.users(self.user['id']).funckeys.templates(self.template['id']).put().assert_updated()
        self.check_provd_has_funckey('1', self.provd_funckeys['1'])
        self.check_provd_has_funckey('2', self.provd_funckeys['2'])

        confd.users(self.user['id']).funckeys.templates(template_2['id']).put().assert_updated()
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
def test_delete_funckey_template_when_user_and_funckey_template_associated(user, funckey_template):
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


class TestBlfFuncKeys(BaseTestFuncKey):

    def setUp(self):
        super(TestBlfFuncKeys, self).setUp()

        user_exten = '1000'
        conf_exten = '4000'
        forward_number = '5000'
        custom_exten = '9999'
        park_pos = 701

        with self.db.queries() as queries:
            conference_id = queries.insert_conference(number=conf_exten)
            callfilter_id = queries.insert_callfilter()
            agent_id = queries.insert_agent(self.user['id'])
            filter_member_id = queries.insert_filter_member(callfilter_id,
                                                            self.user['id'])

        self.confd_funckeys = {
            '1': {'destination': {'type': 'user', 'user_id': self.user['id']}},
            '4': {'destination': {'type': 'conference', 'conference_id': conference_id}},
            '5': {'destination': {'type': 'custom', 'exten': custom_exten}},
            '8': {'destination': {'type': 'service', 'service': 'callrecord'}},
            '9': {'destination': {'type': 'service', 'service': 'incallfilter'}},
            '10': {'destination': {'type': 'service', 'service': 'enablednd'}},
            '14': {'destination': {'type': 'service', 'service': 'enablevm'}},
            '17': {'destination': {'type': 'forward', 'forward': 'noanswer'}},
            '18': {'destination': {'type': 'forward', 'forward': 'busy'}},
            '19': {'destination': {'type': 'forward', 'forward': 'unconditional'}},
            '20': {'destination': {'type': 'forward', 'forward': 'busy', 'exten': forward_number}},
            '23': {'destination': {'type': 'agent', 'action': 'login', 'agent_id': agent_id}},
            '24': {'destination': {'type': 'agent', 'action': 'logout', 'agent_id': agent_id}},
            '25': {'destination': {'type': 'agent', 'action': 'toggle', 'agent_id': agent_id}},
            '26': {'destination': {'type': 'park_position', 'position': park_pos}},
            '29': {'destination': {'type': 'bsfilter', 'filter_member_id': filter_member_id}},
        }

        self.provd_funckeys = {
            '1': {'label': '', 'type': 'blf', 'line': 1, 'value': user_exten},
            '4': {'label': '', 'type': 'blf', 'line': 1, 'value': conf_exten},
            '5': {'label': '', 'type': 'blf', 'line': 1, 'value': custom_exten},
            '8': {'label': '', 'type': 'blf', 'line': 1,
                  'value': '*735{user_id}***226'.format(user_id=self.user['id'])},
            '9': {'label': '', 'type': 'blf', 'line': 1,
                  'value': '*735{user_id}***227'.format(user_id=self.user['id'])},
            '10': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***225'.format(user_id=self.user['id'])},
            '14': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***290'.format(user_id=self.user['id'])},
            '17': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***222'.format(user_id=self.user['id'])},
            '18': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***223'.format(user_id=self.user['id'])},
            '19': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***221'.format(user_id=self.user['id'])},
            '20': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***223*{fwd}'.format(user_id=self.user['id'], fwd=forward_number)},
            '23': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***231***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '24': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***232***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '25': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*735{user_id}***230***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '26': {'label': '', 'type': 'blf', 'line': 1, 'value': str(park_pos)},
            '29': {'label': '', 'type': 'blf', 'line': 1,
                   'value': '*37{member_id}'.format(member_id=filter_member_id)},
        }

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

    def test_when_creating_func_key_that_cannot_be_blf_then_func_key_isnt_blf_in_provd(self):
        position = '1'
        funckey = {'blf': True, 'destination': {'type': 'parking'}}
        provd_funckey = {'label': '', 'type': 'park', 'line': 1, 'value': '700'}

        self.add_funckey_to_user(position, funckey)
        self.check_provd_has_funckey(position, provd_funckey)
