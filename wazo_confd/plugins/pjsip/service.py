# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.helpers import errors
from xivo_dao.resources.asterisk_file import dao as asterisk_file_dao
from xivo_dao.resources.pjsip_transport import dao as pjsip_transport_dao

from wazo_confd.helpers.asterisk import AsteriskConfigurationService
from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier, build_pjsip_transport_notifier
from .validator import build_pjsip_transport_validator

logger = logging.getLogger(__name__)


class PJSIPConfigurationService(AsteriskConfigurationService):

    file_name = 'pjsip.conf'

    def __init__(self, asterisk_file_dao, notifier, pjsip_doc):
        super().__init__(asterisk_file_dao, notifier)
        self.pjsip_doc = pjsip_doc

    def edit(self, section_name, variables):
        for variable in variables:
            if not self.pjsip_doc.is_valid_in_section(section_name, variable.key):
                raise errors.invalid_choice(
                    field='options: invalid variable ({})'.format(variable.key),
                    choices=self.pjsip_doc.get_section_variables(section_name),
                )

        super().edit(section_name, variables)


def build_service(pjsip_doc):
    return PJSIPConfigurationService(asterisk_file_dao, build_notifier(), pjsip_doc)


def build_pjsip_transport_service(pjsip_doc, schema):
    return CRUDService(
        pjsip_transport_dao,
        build_pjsip_transport_validator(pjsip_doc),
        build_pjsip_transport_notifier(schema),
    )
