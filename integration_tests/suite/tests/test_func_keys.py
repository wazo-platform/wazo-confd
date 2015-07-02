import unittest
from hamcrest import assert_that, has_entries, has_key, is_not

from test_api import confd
from test_api import helpers
from test_api import database
from test_api import provd


class TestFuncKey(unittest.TestCase):

    def setUp(self):
        self.db = database.create_helper()
        self.provd = provd.create_helper()

        self.db.recreate()
        self.provd.reset()

        self.user = helpers.user.generate_user()
        self.device = self.setup_device(self.user['id'], '1000')

    def setup_device(self, user_id, exten):
        line = helpers.line.generate_line()
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


class TestUserWithFuncKey(TestFuncKey):

    def setUp(self):
        super(TestUserWithFuncKey, self).setUp()

        self.destination = {'type': 'custom', 'exten': '1234'}
        self.pos = '1'

        self.funckey_url = confd.users(self.user['id']).funckeys(self.pos)
        self.funckey_url.put(destination=self.destination).assert_ok()

    def test_when_getting_position_then_func_key_returned(self):
        expected_funckey = {'label': None,
                            'inherited': False,
                            'blf': False}
        expected_destination = {'type': self.destination['type'],
                                'exten': self.destination['exten'],
                                'href': None}

        response = self.funckey_url.get()

        assert_that(response.item, has_entries(expected_funckey))
        assert_that(response.item['destination'], has_entries(expected_destination))

    def test_when_updating_position_then_func_key_modified_in_provd(self):
        modified_funckey = {'blf': True,
                            'label': 'myfunckey',
                            'destination': {'type': 'park_position',
                                            'position': 701}}

        provd_funckey = {'label': 'myfunckey',
                         'type': 'blf',
                         'line': 1,
                         'value': '701'}

        self.funckey_url.put(**modified_funckey).assert_ok()

        self.check_provd_has_funckey(self.pos, provd_funckey)

    def test_when_deleting_position_then_func_key_removed(self):
        response = self.funckey_url.delete()
        response.assert_ok()

        response = self.funckey_url.get()
        response.assert_status(404)

        self.check_provd_does_not_have_funckey(self.pos)


class TestAllFuncKeyDestinations(TestFuncKey):

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
            '8': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***226'.format(user_id=self.user['id'])},
            '9': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***227'.format(user_id=self.user['id'])},
            '10': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***225'.format(user_id=self.user['id'])},
            '11': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*8'},
            '12': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*34'},
            '13': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*36'},
            '14': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***290'.format(user_id=self.user['id'])},
            '15': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*98'},
            '16': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*92'},
            '17': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***222'.format(user_id=self.user['id'])},
            '18': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***223'.format(user_id=self.user['id'])},
            '19': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***221'.format(user_id=self.user['id'])},
            '20': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***223*{fwd}'.format(user_id=self.user['id'],
                                                                                                            fwd=forward_number)},
            '21': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*1'},
            '22': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*2'},
            '23': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***231***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '24': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***232***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '25': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*735{user_id}***230***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '26': {'label': '', 'type': 'speeddial', 'line': 1, 'value': str(park_pos)},
            '27': {'label': '', 'type': 'park', 'line': 1, 'value': parking},
            '28': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*11{paging}'.format(paging=paging_number)},
            '29': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*37{member_id}'.format(member_id=filter_member_id)},
            '30': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*3'},
            '31': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*20'},
        }

        self.confd_funckeys = {
            '1': {'destination': {'type': 'user', 'user_id': self.user['id']}},
            '2': {'destination': {'type': 'group', 'group_id': group_id}},
            '3': {'destination': {'type': 'queue', 'queue_id': queue_id}},
            '4': {'destination': {'type': 'conference', 'conference_id': conference_id}},
            '5': {'destination': {'type': 'custom', 'exten': custom_exten}},
            '6': {'destination': {'type': 'service', 'service': 'phonestatus'}},
            '7': {'destination': {'type': 'service', 'service': 'recsnd'}},
            '8': {'destination': {'type': 'service', 'service': 'callrecord'}},
            '9': {'destination': {'type': 'service', 'service': 'incallfilter'}},
            '10': {'destination': {'type': 'service', 'service': 'enablednd'}},
            '11': {'destination': {'type': 'service', 'service': 'pickup'}},
            '12': {'destination': {'type': 'service', 'service': 'calllistening'}},
            '13': {'destination': {'type': 'service', 'service': 'directoryaccess'}},
            '14': {'destination': {'type': 'service', 'service': 'enablevm'}},
            '15': {'destination': {'type': 'service', 'service': 'vmusermsg'}},
            '16': {'destination': {'type': 'service', 'service': 'vmuserpurge'}},
            '17': {'destination': {'type': 'forward', 'forward': 'noanswer'}},
            '18': {'destination': {'type': 'forward', 'forward': 'busy'}},
            '19': {'destination': {'type': 'forward', 'forward': 'unconditional'}},
            '20': {'destination': {'type': 'forward', 'forward': 'busy', 'exten': forward_number}},
            '21': {'destination': {'type': 'transfer', 'transfer': 'blind'}},
            '22': {'destination': {'type': 'transfer', 'transfer': 'attended'}},
            '23': {'destination': {'type': 'agent', 'action': 'login', 'agent_id': agent_id}},
            '24': {'destination': {'type': 'agent', 'action': 'logout', 'agent_id': agent_id}},
            '25': {'destination': {'type': 'agent', 'action': 'toggle', 'agent_id': agent_id}},
            '26': {'destination': {'type': 'park_position', 'position': park_pos}},
            '27': {'destination': {'type': 'parking'}},
            '28': {'destination': {'type': 'paging', 'paging_id': paging_id}},
            '29': {'destination': {'type': 'bsfilter', 'filter_member_id': filter_member_id}},
            '30': {'destination': {'type': 'onlinerec'}},
            '31': {'destination': {'type': 'service', 'service': 'fwdundoall'}},
        }

        self.exclude_for_template = ['23', '24', '25', '29']

    def test_when_creating_template_then_all_func_keys_created(self):
        for position in self.exclude_for_template:
            del self.confd_funckeys[position]

        response = confd.funckeys.templates.post(name='mytemplate', keys=self.confd_funckeys)
        funckeys = response.item['keys']

        for pos, expected_funckey in self.confd_funckeys.items():
            self.assert_template_has_funckey(funckeys, pos, expected_funckey)

    def assert_template_has_funckey(self, funckeys, pos, expected):
        base = {'label': None,
                'blf': False,
                'inherited': True}

        assert_that(funckeys, has_key(pos))

        funckey = funckeys[pos]
        assert_that(funckey, has_entries(base))
        assert_that(funckey['destination'], has_entries(expected['destination']))

    def test_when_adding_func_keys_to_user_then_func_keys_added_in_provd(self):
        for pos, funckey in self.confd_funckeys.items():
            provd_funckey = self.provd_funckeys[pos]
            self.add_funckey_to_user(pos, funckey)
            self.check_provd_has_funckey(pos, provd_funckey)


class TestTemplateAssociation(TestFuncKey):

    def setUp(self):
        super(TestTemplateAssociation, self).setUp()

        self.funckeys = {'1': {'destination': {'type': 'custom', 'exten': '9999'}},
                         '2': {'destination': {'type': 'parking'}}}

        self.provd_funckeys = {
            '1': {'label': '', 'type': 'speeddial', 'line': 1, 'value': '9999'},
            '2': {'label': '', 'type': 'park', 'line': 1, 'value': '700'}
        }

        response = confd.funckeys.templates.post(keys=self.funckeys)
        self.template = response.item

        self.association_url = confd.users(self.user['id']).funckeys.templates(self.template['id'])

    def test_given_template_has_func_key_when_associated_then_func_key_added_to_provd(self):
        self.association_url.put().assert_ok()

        for pos, funckey in self.provd_funckeys.items():
            self.check_provd_has_funckey(pos, funckey)

    def test_when_template_dissociated_then_func_key_removed_from_provd(self):
        self.association_url.put().assert_ok()
        self.association_url.delete().assert_ok()

        for pos in self.provd_funckeys.keys():
            self.check_provd_does_not_have_funckey(pos)

    def test_given_user_has_funckey_when_template_associated_then_funckeys_merged(self):
        second_funckey = {'destination': {'type': 'user', 'user_id': self.user['id']}}
        third_funckey = {'destination': {'type': 'service', 'service': 'phonestatus'}}

        first_provd_funckey = self.provd_funckeys['1']
        second_provd_funckey = {'label': '', 'type': 'speeddial', 'line': 1, 'value': '1000'}
        third_provd_fundkey = {'label': '', 'type': 'speeddial', 'line': 1, 'value': '*10'}

        with confd.users(self.user['id']).funckeys as url:
            url(2).put(**second_funckey).assert_ok()
            url(3).put(**third_funckey).assert_ok()

        self.association_url.put().assert_ok()

        self.check_provd_has_funckey('1', first_provd_funckey)
        self.check_provd_has_funckey('2', second_provd_funckey)
        self.check_provd_has_funckey('3', third_provd_fundkey)

    def test_given_template_associated_when_deleting_then_removes_funckeys(self):
        self.association_url.put().assert_ok()

        response = confd.funckeys.templates(self.template['id']).delete()
        response.assert_ok()

        for pos in self.provd_funckeys.keys():
            self.check_provd_does_not_have_funckey(pos)


class TestBlfFuncKeys(TestFuncKey):

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
            '1': {'blf': True, 'destination': {'type': 'user', 'user_id': self.user['id']}},
            '4': {'blf': True, 'destination': {'type': 'conference', 'conference_id': conference_id}},
            '5': {'blf': True, 'destination': {'type': 'custom', 'exten': custom_exten}},
            '8': {'blf': True, 'destination': {'type': 'service', 'service': 'callrecord'}},
            '9': {'blf': True, 'destination': {'type': 'service', 'service': 'incallfilter'}},
            '10': {'blf': True, 'destination': {'type': 'service', 'service': 'enablednd'}},
            '14': {'blf': True, 'destination': {'type': 'service', 'service': 'enablevm'}},
            '17': {'blf': True, 'destination': {'type': 'forward', 'forward': 'noanswer'}},
            '18': {'blf': True, 'destination': {'type': 'forward', 'forward': 'busy'}},
            '19': {'blf': True, 'destination': {'type': 'forward', 'forward': 'unconditional'}},
            '20': {'blf': True, 'destination': {'type': 'forward', 'forward': 'busy', 'exten': forward_number}},
            '23': {'blf': True, 'destination': {'type': 'agent', 'action': 'login', 'agent_id': agent_id}},
            '24': {'blf': True, 'destination': {'type': 'agent', 'action': 'logout', 'agent_id': agent_id}},
            '25': {'blf': True, 'destination': {'type': 'agent', 'action': 'toggle', 'agent_id': agent_id}},
            '26': {'blf': True, 'destination': {'type': 'park_position', 'position': park_pos}},
            '29': {'blf': True, 'destination': {'type': 'bsfilter', 'filter_member_id': filter_member_id}},
        }

        self.provd_funckeys = {
            '1': {'label': '', 'type': 'blf', 'line': 1, 'value': user_exten},
            '4': {'label': '', 'type': 'blf', 'line': 1, 'value': conf_exten},
            '5': {'label': '', 'type': 'blf', 'line': 1, 'value': custom_exten},
            '8': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***226'.format(user_id=self.user['id'])},
            '9': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***227'.format(user_id=self.user['id'])},
            '10': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***225'.format(user_id=self.user['id'])},
            '14': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***290'.format(user_id=self.user['id'])},
            '17': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***222'.format(user_id=self.user['id'])},
            '18': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***223'.format(user_id=self.user['id'])},
            '19': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***221'.format(user_id=self.user['id'])},
            '20': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***223*{fwd}'.format(user_id=self.user['id'],
                                                                                                      fwd=forward_number)},
            '23': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***231***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '24': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***232***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '25': {'label': '', 'type': 'blf', 'line': 1, 'value': '*735{user_id}***230***3{agent_id}'.format(user_id=self.user['id'], agent_id=agent_id)},
            '26': {'label': '', 'type': 'blf', 'line': 1, 'value': str(park_pos)},
            '29': {'label': '', 'type': 'blf', 'line': 1, 'value': '*37{member_id}'.format(member_id=filter_member_id)},
        }

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
