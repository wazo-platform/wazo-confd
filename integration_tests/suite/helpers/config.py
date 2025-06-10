# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

CONTEXT = 'default'
INCALL_CONTEXT = 'from-extern'
OUTCALL_CONTEXT = 'to-extern'
EXTEN_CONFERENCE_RANGE = range(4000, 5000)
EXTEN_GROUP_RANGE = range(2000, 3000)
EXTEN_OUTSIDE_RANGE = str('99999')
EXTEN_QUEUE_RANGE = range(3000, 4000)
EXTEN_USER_RANGE = range(1000, 2000)
MAIN_TENANT = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1'
SUB_TENANT = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee2'
SUB_TENANT2 = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee3'
TOKEN = '00000000-0000-4000-9000-000000070435'
TOKEN_SUB_TENANT = '00000000-0000-4000-9000-000000000222'
DELETED_TENANT = '66666666-6666-4666-8666-666666666666'
CREATED_TENANT = '77777777-7777-4777-8777-777777777777'
USER_UUID = 'd1534a6c-3e35-44db-b4df-0e2957cdea77'
DEFAULT_TENANTS = [
    {
        'uuid': MAIN_TENANT,
        'name': 'name1',
        'slug': 'slug1',
        'parent_uuid': MAIN_TENANT,
    },
    {
        'uuid': SUB_TENANT,
        'name': 'name2',
        'slug': 'slug2',
        'parent_uuid': MAIN_TENANT,
    },
    {
        'uuid': SUB_TENANT2,
        'name': 'name3',
        'slug': 'slug3',
        'parent_uuid': MAIN_TENANT,
    },
]
ALL_TENANTS = DEFAULT_TENANTS + [
    {
        'uuid': DELETED_TENANT,
        'name': 'name3',
        'slug': 'slug3',
        'parent_uuid': MAIN_TENANT,
    },
    {
        'uuid': CREATED_TENANT,
        'name': 'name4',
        'slug': 'slug4',
        'parent_uuid': MAIN_TENANT,
    },
]
