# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.access_feature import dao as access_feature_dao

from xivo_dao.helpers import errors
from wazo_confd.helpers.validator import Validator, ValidationGroup


class CreateAccessFeatureUniqueHostValidator(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, access_feature):
        existing = self.dao.find_by(
            host=access_feature.host, feature=access_feature.feature
        )

        if existing:
            raise errors.resource_exists(
                'AccessFeatures',
                host=access_feature.host,
                feature=access_feature.feature,
            )


class EditAccessFeatureUniqueHostValidator(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, access_feature):
        existing = self.dao.find_by(
            host=access_feature.host, feature=access_feature.feature
        )

        if existing:
            if existing.id != access_feature.id:
                raise errors.resource_exists(
                    'AccessFeatures',
                    host=access_feature.host,
                    feature=access_feature.feature,
                )


def build_validator():
    return ValidationGroup(
        create=[CreateAccessFeatureUniqueHostValidator(access_feature_dao)],
        edit=[EditAccessFeatureUniqueHostValidator(access_feature_dao)],
    )
