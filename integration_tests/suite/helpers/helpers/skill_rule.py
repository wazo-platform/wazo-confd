# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_skill_rule(**parameters):
    return add_skill_rule(**parameters)


def add_skill_rule(**parameters):
    response = confd.queues.skillrules.post(parameters)
    return response.item


def delete_skill_rule(skill_rule_id, check=False):
    response = confd.queues.skillrules(skill_rule_id).delete()
    if check:
        response.assert_ok()
