# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random

CONTEXT = 'default'
INCALL_CONTEXT = 'from-extern'
OUTCALL_CONTEXT = 'to-extern'
EXTENSION_RANGE = list(range(1000, 5001))
ENTITY_NAME = 'xivotest'
EXTEN_OUTSIDE_RANGE = str('99999')


def gen_group_exten():
    return str(random.randint(2000, 3000))


def gen_conference_exten():
    return str(random.randint(4000, 5000))
