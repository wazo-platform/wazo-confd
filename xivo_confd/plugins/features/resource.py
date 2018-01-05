# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from marshmallow import fields, pre_dump, post_load, pre_load, post_dump, validates_schema
from marshmallow.validate import Length, NoneOf
from marshmallow.exceptions import ValidationError

from xivo_dao.alchemy.features import Features
from xivo_dao.resources.features.search import PARKING_OPTIONS, FUNC_KEY_FEATUREMAP_FOREIGN_KEY

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource

PARKING_ERROR = "The parking options can only be defined with the parkinglots API"


class AsteriskOptionSchema(BaseSchema):
    key = fields.String(validate=(Length(max=128)),
                        required=True,
                        attribute='var_name')
    value = fields.String(validate=(Length(max=255)),
                          required=True,
                          attribute='var_val')


class FeaturesConfigurationSchema(BaseSchema):
    options = fields.Nested(AsteriskOptionSchema, many=True, required=True)

    @pre_load
    def convert_options_to_collection(self, data):
        options = data.get('options')
        if isinstance(options, dict):
            data['options'] = [{'key': key, 'value': value} for key, value in options.iteritems()]
        return data

    @post_dump
    def convert_options_to_dict(self, data):
        data['options'] = {option['key']: option['value'] for option in data['options']}
        return data

    @pre_dump
    def add_envelope(self, data):
        return {'options': data}

    @post_load
    def remove_envelope(self, data):
        return data['options']


class FeaturesGeneralOptionSchema(AsteriskOptionSchema):
    key = fields.String(validate=(Length(max=128),
                                  NoneOf(PARKING_OPTIONS, error=PARKING_ERROR)),
                        required=True,
                        attribute='var_name')


class FeaturesGeneralSchema(FeaturesConfigurationSchema):
    options = fields.Nested(FeaturesGeneralOptionSchema, many=True, required=True)


class FeaturesFeaturemapSchema(FeaturesConfigurationSchema):
    options = fields.Nested(AsteriskOptionSchema, many=True, required=True)

    @validates_schema
    def _validate_required_options(self, data):
        keys = [option.get('var_name') for option in data.get('options', {})]

        for required in FUNC_KEY_FEATUREMAP_FOREIGN_KEY:
            if required not in keys:
                raise ValidationError('The following option are required: {}'.format(required), 'options')


class FeaturesConfigurationList(ConfdResource):
    model = Features
    schema = FeaturesConfigurationSchema
    section_name = None

    def __init__(self, service):
        super(FeaturesConfigurationList, self).__init__()
        self.service = service

    def get(self):
        options = self.service.list(section=self.section_name)
        return self.schema().dump(options).data

    def put(self):
        form = self.schema().load(request.get_json()).data
        variables = [self.model(**option) for option in form]
        self.service.edit(self.section_name, variables)
        return '', 204


class FeaturesApplicationmapList(FeaturesConfigurationList):
    section_name = 'applicationmap'

    @required_acl('confd.asterisk.features.applicationmap.get')
    def get(self):
        return super(FeaturesApplicationmapList, self).get()

    @required_acl('confd.asterisk.features.applicationmap.update')
    def put(self):
        return super(FeaturesApplicationmapList, self).put()


class FeaturesFeaturemapList(FeaturesConfigurationList):
    section_name = 'featuremap'
    schema = FeaturesFeaturemapSchema

    @required_acl('confd.asterisk.features.featuremap.get')
    def get(self):
        return super(FeaturesFeaturemapList, self).get()

    @required_acl('confd.asterisk.features.featuremap.update')
    def put(self):
        return super(FeaturesFeaturemapList, self).put()


class FeaturesGeneralList(FeaturesConfigurationList):
    section_name = 'general'
    schema = FeaturesGeneralSchema

    @required_acl('confd.asterisk.features.general.get')
    def get(self):
        return super(FeaturesGeneralList, self).get()

    @required_acl('confd.asterisk.features.general.update')
    def put(self):
        return super(FeaturesGeneralList, self).put()
