# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(context_id, context_ids, check=True):
    contexts = [{'id': c_id} for c_id in context_ids]
    response = confd.contexts(context_id).contexts.put(contexts=contexts)
    if check:
        response.assert_ok()


def dissociate(context_id, check=True):
    response = confd.contexts(context_id).contexts.put(contexts=[])
    if check:
        response.assert_ok()
