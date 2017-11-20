# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from . import confd


@fixtures.queue()
@fixtures.extension()
def test_delete_extension_associated_to_queue(queue, extension):
    with a.queue_extension(queue, extension):
        response = confd.extensions(extension['id']).delete()
        response.assert_match(400, e.resource_associated('Extension', 'queue'))
