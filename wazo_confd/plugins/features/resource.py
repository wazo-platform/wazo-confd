# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import (
    fields,
    post_dump,
    post_load,
    pre_dump,
    pre_load,
    validates_schema,
)
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, NoneOf
from xivo_dao.alchemy.features import Features
from xivo_dao.resources.features.search import (
    FUNC_KEY_APPLICATIONMAP_FOREIGN_KEY,
    FUNC_KEY_FEATUREMAP_FOREIGN_KEY,
)

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource

PARKING_ERROR = "The parking options can only be defined with the parkinglots API"
PARKING_OPTIONS = [
    'comebacktoorigin',
    'context',
    'courtesytone',
    'findslot',
    'parkedcallhangup',
    'parkedcallrecording',
    'parkedcallreparking',
    'parkedcalltransfers',
    'parkeddynamic',
    'parkedmusicclass',
    'parkedplay',
    'parkext',
    'parkinghints',
    'parkingtime',
    'parkpos',
]


class AsteriskOptionSchema(BaseSchema):
    key = fields.String(validate=(Length(max=128)), required=True, attribute='var_name')
    value = fields.String(
        validate=(Length(max=255)), required=True, attribute='var_val'
    )


class FeaturesConfigurationSchema(BaseSchema):
    options = Nested(AsteriskOptionSchema, many=True, required=True)

    @pre_load
    def convert_options_to_collection(self, data, **kwargs):
        options = data.get('options')
        if isinstance(options, dict):
            data['options'] = [
                {'key': key, 'value': value} for key, value in options.items()
            ]
        return data

    @post_dump
    def convert_options_to_dict(self, data, **kwargs):
        data['options'] = {option['key']: option['value'] for option in data['options']}
        return data

    @pre_dump
    def add_envelope(self, data, **kwargs):
        return {'options': data}

    @post_load
    def remove_envelope(self, data, **kwargs):
        return data['options']


class FeaturesGeneralOptionSchema(AsteriskOptionSchema):
    key = fields.String(
        validate=(Length(max=128), NoneOf(PARKING_OPTIONS, error=PARKING_ERROR)),
        required=True,
        attribute='var_name',
    )


class FeaturesGeneralSchema(FeaturesConfigurationSchema):
    options = Nested(FeaturesGeneralOptionSchema, many=True, required=True)


class FeaturesFeaturemapSchema(FeaturesConfigurationSchema):
    options = Nested(AsteriskOptionSchema, many=True, required=True)

    @validates_schema
    def _validate_required_options(self, data, **kwargs):
        keys = [option.get('var_name') for option in data.get('options', {})]

        for required in FUNC_KEY_FEATUREMAP_FOREIGN_KEY:
            if required not in keys:
                raise ValidationError(
                    'The following option are required: {}'.format(required),
                    field_name='options',
                )


class FeaturesApplicationmapSchema(FeaturesConfigurationSchema):
    options = Nested(AsteriskOptionSchema, many=True, required=True)

    @validates_schema
    def _validate_required_options(self, data, **kwargs):
        keys = [option.get('var_name') for option in data.get('options', {})]

        for required in FUNC_KEY_APPLICATIONMAP_FOREIGN_KEY:
            if required not in keys:
                raise ValidationError(
                    'The following option are required: {}'.format(required),
                    field_name='options',
                )


class FeaturesConfigurationList(ConfdResource):
    model = Features
    schema = FeaturesConfigurationSchema
    section_name = None

    def __init__(self, service):
        super().__init__()
        self.service = service

    def get(self):
        options = self.service.list(section=self.section_name)
        return self.schema().dump(options)

    def put(self):
        form = self.schema().load(request.get_json(force=True))
        variables = [self.model(**option) for option in form]
        self.service.edit(self.section_name, variables)
        return '', 204


class FeaturesApplicationmapList(FeaturesConfigurationList):
    section_name = 'applicationmap'
    schema = FeaturesApplicationmapSchema

    @required_master_tenant()
    @required_acl('confd.asterisk.features.applicationmap.get')
    def get(self):
        return super().get()

    @required_master_tenant()
    @required_acl('confd.asterisk.features.applicationmap.update')
    def put(self):
        return super().put()


class FeaturesFeaturemapList(FeaturesConfigurationList):
    section_name = 'featuremap'
    schema = FeaturesFeaturemapSchema

    @required_master_tenant()
    @required_acl('confd.asterisk.features.featuremap.get')
    def get(self):
        return super().get()

    @required_master_tenant()
    @required_acl('confd.asterisk.features.featuremap.update')
    def put(self):
        return super().put()


class FeaturesGeneralList(FeaturesConfigurationList):
    section_name = 'general'
    schema = FeaturesGeneralSchema

    @required_master_tenant()
    @required_acl('confd.asterisk.features.general.get')
    def get(self):
        return super().get()

    @required_master_tenant()
    @required_acl('confd.asterisk.features.general.update')
    def put(self):
        return super().put()
