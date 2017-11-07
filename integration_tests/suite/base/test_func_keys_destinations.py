# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+


from hamcrest import assert_that, contains_inanyorder
from . import confd, BaseIntegrationTest


def test_get_destinations():
    expected_result = [
        {'type': 'park_position',
         'parameters': [{'name': 'position'}]},
        {'type': 'agent',
         'parameters': [{'values': ['login',
                                    'logout',
                                    'toggle'],
                         'name': 'action'},
                        {'name': 'agent_id'}]},
        {'type': 'onlinerec',
         'parameters': []},
        {'type': 'user',
         'parameters': [{'name': 'user_id',
                         'collection': 'https://localhost:{}/1.1/users'.format(
                             BaseIntegrationTest.service_port(9486, 'confd')
                         )}]},
        {'type': 'parking',
         'parameters': []},
        {'type': 'conference',
         'parameters': [{'name': 'conference_id'}]},
        {'type': 'group',
         'parameters': [{'name': 'group_id'}]},
        {'type': 'service',
         'parameters': [{'values': ['enablevm',
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
                                    'enablednd'],
                         'name': 'service'}]},
        {'type': 'transfer',
         'parameters': [{'values': ['blind',
                                    'attended'],
                         'name': 'transfer'}]},
        {'type': 'bsfilter',
         'parameters': [{'name': 'filter_member_id'}]},
        {'type': 'custom',
         'parameters': [{'name': 'exten'}]},
        {'type': 'queue',
         'parameters': [{'name': 'queue_id'}]},
        {'type': 'paging',
         'parameters': [{'name': 'paging_id'}]},
        {'type': 'forward',
         'parameters': [{'values': ['busy',
                                    'noanswer',
                                    'unconditional'],
                         'name': 'forward'},
                        {'name': 'exten'}]}
    ]

    response = confd.funckeys.destinations.get()
    response.assert_ok()

    assert_that(response.item, contains_inanyorder(*expected_result))
