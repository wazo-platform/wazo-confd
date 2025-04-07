# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.feature_extension import dao as feature_extension_dao

from wazo_confd.helpers.validator import ValidationGroup, Validator


class ExtenAvailableOnUpdateValidator(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, extension):
        existing = self.dao.find_by(exten=extension.exten)
        if existing and existing.uuid != extension.uuid:
            raise errors.resource_exists('FeatureExtension', exten=extension.exten)


def build_validator():
    return ValidationGroup(
        edit=[ExtenAvailableOnUpdateValidator(feature_extension_dao)]
    )
