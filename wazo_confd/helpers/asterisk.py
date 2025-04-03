# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import gzip
import json

from flask import request

from marshmallow import fields, pre_dump, post_load, pre_load, post_dump
from marshmallow.validate import Length

from wazo.rest_api_helpers import APIException
from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable
from xivo_dao.helpers import errors

from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.restful import ConfdResource
from wazo_confd.helpers.validator import Validator

from .mallow import Nested

logger = logging.getLogger(__name__)


class AsteriskOptionSchema(BaseSchema):
    key = fields.String(validate=Length(max=255), required=True)
    value = fields.String(required=True)


class AsteriskConfigurationSchema(BaseSchema):
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


class AsteriskConfigurationList(ConfdResource):
    model = AsteriskFileVariable
    schema = AsteriskConfigurationSchema
    section_name = None

    def __init__(self, service):
        super().__init__()
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


class PJSIPDocError(APIException):
    def __init__(self, msg):
        super().__init__(400, msg, None, None, None)


class PJSIPDoc:
    _internal_fields = set(['type'])

    def __init__(self, filename):
        logger.debug('%s initialized with file %s', self.__class__.__name__, filename)
        self._filename = filename
        self._content = None

    def get(self):
        return self.content

    def is_valid_in_section(self, section_name, variable):
        if section_name in ('aor', 'endpoint'):
            if variable.startswith('@'):
                return True

        return variable in self.get_section_variables(section_name)

    def get_section_variables(self, section_name):
        # NOTE(fblackburn): Some sections are not documented and must be hardcoded
        if section_name == 'identify':
            return ['match', 'endpoint', 'srv_lookups', 'match_header']
        if section_name == 'registration':
            return [
                'auth_rejection_permanent',
                'client_uri',
                'contact_user',
                'contact_header_params',
                'expiration',
                'max_retries',
                'outbound_proxy',
                'retry_interval',
                'server_uri',
                'forbidden_retry_interval',
                'fatal_retry_interval',
                'line',
                'server_uri',
                'transport',
                'support_path',
                'support_outbound',
            ]
        return self.content.get(section_name, {}).keys()

    @property
    def content(self):
        if self._content is None:
            self._content = self._fetch()
            for section_name in self._content.keys():
                for field in self._internal_fields:
                    self._content[section_name].pop(field, None)
        return self._content

    def _fetch(self):
        try:
            logger.debug(
                'refreshing %s cached file from %s',
                self.__class__.__name__,
                self._filename,
            )
            with gzip.open(self._filename, 'rb') as f:
                return json.load(f)
        except Exception as e:
            logger.info('failed to read PJSIP doc %s %s', self._filename, e)
            raise PJSIPDocError('failed to read PJSIP JSON documentation')


class PJSIPDocValidator(Validator):
    def __init__(self, field, section, pjsip_doc):
        self.field = field
        self.pjsip_doc = pjsip_doc
        self.section = section

    def validate(self, model):
        self._validate(model)

    def _validate(self, model):
        values = getattr(model, self.field, [])
        option_names = [value[0] for value in values]
        for option_name in option_names:
            if not self.pjsip_doc.is_valid_in_section(self.section, option_name):
                raise errors.invalid_choice(
                    field='{}: invalid variable ({})'.format(self.field, option_name),
                    choices=self.pjsip_doc.get_section_variables(self.section),
                )
