# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder

from . import confd, BaseIntegrationTest


def test_get_destinations():
    response = confd.funckeys.destinations.get()
    response.assert_ok()

    assert_that(
        response.item,
        contains_inanyorder(
             {
                 'type': 'agent',
                 'parameters': [
                     {'values': ['login', 'logout', 'toggle'], 'name': 'action'},
                     {'name': 'agent_id'},
                 ],
             },
             {
                 'type': 'bsfilter',
                 'parameters': [{'name': 'filter_member_id'}],
             },
             {
                 'type': 'conference',
                 'parameters': [{'name': 'conference_id'}],
             },
             {
                 'type': 'custom',
                 'parameters': [{'name': 'exten'}],
             },
             {
                 'type': 'forward',
                 'parameters': [
                     {'values': ['busy', 'noanswer', 'unconditional'], 'name': 'forward'},
                     {'name': 'exten'},
                 ],
             },
             {
                 'type': 'group',
                 'parameters': [{'name': 'group_id'}],
             },
             {
                 'type': 'groupmember',
                 'parameters': [
                     {'name': 'action', 'values': ['join', 'leave', 'toggle']},
                     {'name': 'group_id'},
                 ],
             },
             {
                 'type': 'onlinerec',
                 'parameters': [],
             },
             {
                 'type': 'paging',
                 'parameters': [{'name': 'paging_id'}],
             },
             {
                 'type': 'park_position',
                 'parameters': [{'name': 'position'}],
             },
             {
                 'type': 'parking',
                 'parameters': []
             },
             {
                 'type': 'queue',
                 'parameters': [{'name': 'queue_id'}],
             },
             {
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
             },
             {
                 'type': 'transfer',
                 'parameters': [{'values': ['blind', 'attended'], 'name': 'transfer'}]
             },
             {
                 'type': 'user',
                 'parameters': [
                     {
                         'name': 'user_id',
                         'collection': 'https://localhost:{}/1.1/users'.format(
                             BaseIntegrationTest.service_port(9486, 'confd')
                         ),
                     },
                 ],
             }
        )
    )
