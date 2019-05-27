# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, has_entries

from . import confd, BaseIntegrationTest


def test_get_destinations():
    response = confd.funckeys.destinations.get()
    response.assert_ok()

    assert_that(
        response.item,
        contains_inanyorder(
             has_entries({
                 'type': 'agent',
                 'parameters': contains_inanyorder(
                     {'values': ['login', 'logout', 'toggle'], 'name': 'action'},
                     {'name': 'agent_id'},
                 ),
             }),
             has_entries({
                 'type': 'bsfilter',
                 'parameters': [{'name': 'filter_member_id'}],
             }),
             has_entries({
                 'type': 'conference',
                 'parameters': [{'name': 'conference_id'}],
             }),
             has_entries({
                 'type': 'custom',
                 'parameters': [{'name': 'exten'}],
             }),
             has_entries({
                 'type': 'forward',
                 'parameters': contains_inanyorder(
                     {'values': ['busy', 'noanswer', 'unconditional'], 'name': 'forward'},
                     {'name': 'exten'},
                 ),
             }),
             has_entries({
                 'type': 'group',
                 'parameters': [{'name': 'group_id'}],
             }),
             has_entries({
                 'type': 'groupmember',
                 'parameters': contains_inanyorder(
                     {'name': 'action', 'values': ['join', 'leave', 'toggle']},
                     {'name': 'group_id'},
                 ),
             }),
             has_entries({
                 'type': 'onlinerec',
                 'parameters': [],
             }),
             has_entries({
                 'type': 'paging',
                 'parameters': [{'name': 'paging_id'}],
             }),
             has_entries({
                 'type': 'park_position',
                 'parameters': [{'name': 'position'}],
             }),
             has_entries({
                 'type': 'parking',
                 'parameters': []
             }),
             has_entries({
                 'type': 'queue',
                 'parameters': [{'name': 'queue_id'}],
             }),
             has_entries({
                 'type': 'service',
                 'parameters': [
                     {'values': [
                         'enablevm',
                         'vmusermsg',
                         'vmuserpurge',
                         'phonestatus',
                         'recsnd',
                         'calllistening',
                         'directoryaccess',
                         'fwdundoall',
                         'pickup',
                         'callrecord',
                         'incallfilter',
                         'enablednd'
                     ], 'name': 'service'}
                 ],
             }),
             has_entries({
                 'type': 'transfer',
                 'parameters': [{'values': ['blind', 'attended'], 'name': 'transfer'}]
             }),
             has_entries({
                 'type': 'user',
                 'parameters': [
                     {
                         'name': 'user_id',
                         'collection': 'https://localhost:{}/1.1/users'.format(
                             BaseIntegrationTest.service_port(9486, 'confd')
                         ),
                     },
                 ],
             }),
        )
    )
