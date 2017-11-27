# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.resource import CRUDService

from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.resources.register_sip import dao as register_sip_dao

from .validator import build_validator
from .notifier import build_notifier


class RegisterSIPService(CRUDService):

    def create(self, register_sip):
        resource = StaticSIP(filename='sip.conf',
                             category='general',
                             var_name='register',
                             var_val=register_sip['var_val'])
        if register_sip.get('enabled'):
            resource.enabled = register_sip.get('enabled')
        return super(RegisterSIPService, self).create(resource)


def build_service():
    return RegisterSIPService(register_sip_dao,
                              build_validator(),
                              build_notifier())
