# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import SkillItem, SkillList
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            SkillList,
            '/agents/skills',
            resource_class_args=(service,)
        )

        api.add_resource(
            SkillItem,
            '/agents/skills/<int:id>',
            endpoint='skills',
            resource_class_args=(service,)
        )
