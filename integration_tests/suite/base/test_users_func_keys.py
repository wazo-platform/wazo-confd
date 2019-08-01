# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
    has_key,
    is_not,
)

from . import confd, provd
from .test_func_keys import error_funckey_checks, error_funckeys_checks
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)

FAKE_ID = 999999999


def test_put_errors():
    with fixtures.user() as user:
        fake_user = confd.users(FAKE_ID).funckeys(1).put
        s.check_resource_not_found(fake_user, 'User')

        url = confd.users(user['uuid']).funckeys(1).put
        error_funckey_checks(url)

        fake_user = confd.users(FAKE_ID).funckeys.put
        s.check_resource_not_found(fake_user, 'User')

        url = confd.users(user['uuid']).funckeys.put
        error_funckeys_checks(url)



def test_delete_errors():
    fake_user = confd.users(FAKE_ID).funckeys(1).delete
    s.check_resource_not_found(fake_user, 'User')

    # This should raise an error
    # fake_funckey = confd.users(self.user['id']).funckeys(FAKE_ID).delete
    # s.check_resource_not_found(fake_funckey, 'FuncKey')


def test_get_errors():
    with fixtures.user() as user:
        fake_user_1 = confd.users(FAKE_ID).funckeys.get
        fake_user_2 = confd.users(FAKE_ID).funckeys(1).get
        fake_funckey = confd.users(user['uuid']).funckeys(FAKE_ID).get

        s.check_resource_not_found(fake_user_1, 'User')
        s.check_resource_not_found(fake_user_2, 'User')
        s.check_resource_not_found(fake_funckey, 'FuncKey')



def test_list():
    with fixtures.user() as user, fixtures.line_sip() as line_sip, fixtures.extension() as extension, fixtures.device() as device:
        with a.line_extension(line_sip, extension), a.user_line(user, line_sip), a.line_device(line_sip, device):
            destination_1 = {'type': 'custom', 'exten': '1234'}
            destination_2 = {'type': 'custom', 'exten': '456'}
            destination_3 = {'type': 'custom', 'exten': '789'}
            destination_4 = {'type': 'custom', 'exten': '012'}
            confd.users(user['id']).funckeys(1).put(destination=destination_1)
            confd.users(user['id']).funckeys(2).put(destination=destination_2)
            confd.users(user['id']).funckeys(3).put(destination=destination_3)
            template_parameters = {'name': 'pos4',
                                   'keys': {'4': {'destination': destination_4}}}
            template = confd.funckeys.templates.post(**template_parameters).item
            confd.users(user['id']).funckeys.templates(template['id']).put()

            response = confd.users(user['id']).funckeys.get()
            assert_that(
                response.item,
                has_entries(
                    keys=has_entries({
                        '1': has_entries(destination=has_entries(destination_1)),
                        '2': has_entries(destination=has_entries(destination_2)),
                        '3': has_entries(destination=has_entries(destination_3)),
                        '4': has_entries(destination=has_entries(destination_4)),
                    })
                )
            )


def test_put_position():
    with fixtures.user() as user, fixtures.line_sip() as line_sip, fixtures.extension() as extension, fixtures.device() as device:
        modified_funckey = {
            'blf': False,
            'label': 'myfunckey',
            'destination': {'type': 'park_position', 'position': 701}
        }
        uuid_funckey = {
            'blf': False,
            'label': 'myfunckey',
            'destination': {'type': 'park_position', 'position': 702}
        }

        provd_funckey = {
            'label': 'myfunckey',
            'type': 'speeddial',
            'line': 1,
            'value': '701',
        }
        provd_uuid_funckey = {
            'label': 'myfunckey',
            'type': 'speeddial',
            'line': 1,
            'value': '702',
        }
        position = 1

        with a.line_extension(line_sip, extension), a.user_line(user, line_sip), a.line_device(line_sip, device):
            destination = {'type': 'custom', 'exten': '1234'}
            confd.users(user['id']).funckeys(position).put(destination=destination)

            response = confd.users(user['id']).funckeys(position).put(modified_funckey)
            response.assert_updated()
            check_provd_has_funckey(device, position, provd_funckey)

            response = confd.users(user['uuid']).funckeys(position).put(uuid_funckey)
            response.assert_updated()
            check_provd_has_funckey(device, position, provd_uuid_funckey)



def check_provd_has_funckey(device, position, funckey):
    position = str(position)
    config = provd.configs.get(device['id'])
    funckeys = config['raw_config']['funckeys']

    assert_that(funckeys, has_key(position))
    assert_that(funckeys[position], has_entries(funckey))


def test_delete_position():
    with fixtures.user() as user, fixtures.line_sip() as line_sip, fixtures.extension() as extension, fixtures.device() as device:
        destination_id = {'type': 'custom', 'exten': '1234'}
        destination_uuid = {'type': 'custom', 'exten': '1235'}
        position_id = 1
        position_uuid = 2
        with a.line_extension(line_sip, extension), a.user_line(user, line_sip), a.line_device(line_sip, device):
            confd.users(user['id']).funckeys(position_id).put(destination=destination_id).assert_updated()
            confd.users(user['id']).funckeys(position_uuid).put(destination=destination_uuid).assert_updated()

            response = confd.users(user['id']).funckeys(position_id).delete()
            response.assert_deleted()
            response = confd.users(user['uuid']).funckeys(position_uuid).delete()
            response.assert_deleted()

            response = confd.users(user['id']).funckeys(position_id).get().assert_status(404)
            response = confd.users(user['uuid']).funckeys(position_uuid).get().assert_status(404)
            check_provd_does_not_have_funckey(device, position_id)
            check_provd_does_not_have_funckey(device, position_uuid)



def check_provd_does_not_have_funckey(device, position):
    position = str(position)
    config = provd.configs.get(device['id'])
    funckeys = config['raw_config']['funckeys']

    assert_that(funckeys, is_not(has_key(position)))


def test_get_position():
    with fixtures.user() as user:
        funckey = {'label': 'example',
                   'blf': True,
                   'destination': {'type': 'custom',
                                   'exten': '1234'}}

        confd.users(user['id']).funckeys(1).put(funckey).assert_updated()

        expected_funckey = funckey
        expected_funckey['destination']['href'] = None
        expected_funckey['inherited'] = False

        response = confd.users(user['id']).funckeys(1).get()
        assert_that(response.item, has_entries(expected_funckey))

        response = confd.users(user['uuid']).funckeys(1).get()
        assert_that(response.item, has_entries(expected_funckey))



def test_put_error_on_duplicate_destination():
    with fixtures.user() as user:
        parameters = {'name': 'duplicate_dest',
                      'keys': {'1': {'destination': {'type': 'custom', 'exten': '123'}},
                               '2': {'destination': {'type': 'custom', 'exten': '123'}}}}

        response = confd.users(user['id']).funckeys.put(**parameters)
        response.assert_status(400)



def test_error_when_user_are_not_bs_filter_member():
    with fixtures.user() as user:
        parameters = {'name': 'validate_bsfilter',
                      'keys': {'1': {'destination': {'type': 'bsfilter', 'filter_member_id': '123'}}}}

        response = confd.users(user['id']).funckeys.put(**parameters)
        response.assert_match(400, e.missing_association('User', 'BSFilter'))



def test_when_line_has_another_position_then_func_key_generated():
    with fixtures.user() as user, fixtures.line_sip(position=2) as line_sip, fixtures.extension() as extension, fixtures.device() as device:
        with a.line_extension(line_sip, extension), a.user_line(user, line_sip), a.line_device(line_sip, device):
            destination = {'type': 'custom', 'exten': '1234'}
            confd.users(user['id']).funckeys(1).put(destination=destination).assert_updated()
            response = confd.users(user['id']).funckeys(1).get()
            assert_that(response.item['destination'], has_entries(destination))


def test_when_move_funckey_position_then_no_duplicate_error():
    with fixtures.user() as user, fixtures.line_sip() as line_sip, fixtures.extension() as extension, fixtures.device() as device:
        with a.line_extension(line_sip, extension), a.user_line(user, line_sip), a.line_device(line_sip, device):
            destination = {'type': 'custom', 'exten': '1234'}
            confd.users(user['id']).funckeys(1).put(destination=destination).assert_updated()

            response = confd.users(user['id']).funckeys.put(keys={'2': {'destination': destination}})
            response.assert_updated()
            check_provd_does_not_have_funckey(device, 1)
            check_provd_has_funckey(device, 2, {'label': '', 'type': 'blf', 'line': 1, 'value': '1234'})


def test_edit_all_parameters():
    # Done in test_func_keys.py
    pass
