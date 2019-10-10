# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from marshmallow import EXCLUDE, fields, pre_dump, post_load, pre_load, post_dump
from marshmallow.validate import Length

from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable
from xivo_dao.helpers import errors

from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.restful import ConfdResource


class AsteriskOptionSchema(BaseSchema):
    key = fields.String(validate=Length(max=255), required=True)
    value = fields.String(required=True)


class AsteriskConfigurationSchema(BaseSchema):
    options = fields.Nested(
        AsteriskOptionSchema, many=True, required=True, unknown=EXCLUDE
    )

    @pre_load
    def convert_options_to_collection(self, data):
        options = data.get('options')
        if isinstance(options, dict):
            data['options'] = [
                {'key': key, 'value': value} for key, value in options.items()
            ]
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


class AsteriskConfigurationList(ConfdResource):
    model = AsteriskFileVariable
    schema = AsteriskConfigurationSchema
    section_name = None

    def __init__(self, service):
        super(AsteriskConfigurationList, self).__init__()
        self.service = service

    def get(self):
        options = self.service.list(self.section_name)
        return self.schema().dump(options)

    def put(self):
        form = self.schema().load(request.get_json())
        variables = [self.model(**option) for option in form]
        self.service.edit(self.section_name, variables)
        return '', 204


class AsteriskConfigurationService:

    file_name = None

    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def list(self, section_name):
        file_ = self.dao.find_by(name=self.file_name)
        if not file_:
            return []

        section = file_.sections.get(section_name)
        if not section:
            return []

        return section.variables

    def edit(self, section_name, variables):
        file_ = self.dao.find_by(name=self.file_name)
        if not file_:
            raise errors.not_found('AsteriskFile', name=self.file_name)

        section = file_.sections.get(section_name)
        if not section:
            raise errors.not_found('AsteriskFileSection', section=section_name)

        self.dao.edit_section_variables(section, variables)
        self.notifier.edited(section_name, file_)
