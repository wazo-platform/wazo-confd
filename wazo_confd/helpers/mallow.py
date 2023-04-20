# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from flask import url_for
from flask_restful import abort
from marshmallow import EXCLUDE, Schema, fields, pre_load, validate
from marshmallow.exceptions import ValidationError


class BaseSchema(Schema):
    def __init__(self, handle_error=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if handle_error:

            def handle_error_fn(error, data, **kwargs):
                # Ugly hack to keep the same error message from python2 to python3
                # The message can be a dictionary and we do not want to cast it to string,
                # because there are some logic with the `type` in common.py
                if len(error.args):
                    message = error.args[0]
                else:
                    message = str(error)
                return abort(400, message=message)

            self.handle_error = handle_error_fn

    def on_bind_field(self, field_name, field_obj):
        # Without this, the nested schema handle error and abort. So the error
        # message will not include parent key and the rest of the parent schema
        # will not be validated
        self._inherit_handle_error(field_obj)

    def _inherit_handle_error(self, field_obj):
        if isinstance(field_obj, fields.Nested):
            field_obj.schema.handle_error = super().handle_error
        if isinstance(field_obj, fields.List):
            self._inherit_handle_error(field_obj.inner)

    @pre_load
    def ensure_dict(self, data, **kwargs):
        return data or {}

    class Meta:
        ordered = True
        unknown = EXCLUDE


class Nested(fields.Nested):
    def _deserialize(self, value, attr, data, partial=None, **kwargs):
        # wazo-confd only support partial on first layer, not through nested fields
        fake_partial = False
        return super()._deserialize(value, attr, data, partial=fake_partial, **kwargs)


class UserSchemaUUIDLoad(BaseSchema):
    uuid = fields.String(required=True)


class UsersUUIDSchema(BaseSchema):
    users = fields.Nested(UserSchemaUUIDLoad, many=True, required=True)


class StrictBoolean(fields.Boolean):
    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, bool):
            raise self.make_error('invalid')
        return value


class Link(fields.Field):
    _CHECK_ATTRIBUTE = False

    def __init__(self, resource, route=None, field='id', target=None, **kwargs):
        super().__init__(dump_only=True, **kwargs)
        self.resource = resource
        self.route = route or resource
        self.field = field
        self.target = target or field

    def _serialize(self, value, key, obj):
        value = self.extract_value(obj)
        if value:
            options = {self.target: value, '_external': True}
            url = url_for(self.route, **options)
            return {'rel': self.resource, 'href': url}

    def extract_value(self, obj):
        if isinstance(obj, dict):
            return obj.get(self.field)
        return getattr(obj, self.field)


class ListLink(fields.Field):
    _CHECK_ATTRIBUTE = False

    def __init__(self, *links, **kwargs):
        super().__init__(dump_only=True, **kwargs)
        self.links = links

    def _serialize(self, value, key, obj):
        output = []
        for link in self.links:
            link_obj = link.serialize(key, obj)
            if link_obj:
                output.append(link_obj)
        return output


class PJSIPSectionOption(fields.List):
    DEFAULT_OPTION_REGEX = r"^[a-zA-Z0-9-_\/\.:]*$"

    def __init__(self, option_regex=DEFAULT_OPTION_REGEX, **kwargs):
        kwargs['validate'] = [validate.Length(min=1, max=4092)]
        if option_regex:
            kwargs['validate'].append(validate.Regexp(option_regex))

        super().__init__(
            fields.String(**kwargs),
            validate=validate.Length(min=2, max=2),
        )


class AsteriskSection:
    DEFAULT_REGEX = re.compile(r'^[-_.a-zA-Z0-9]+$')
    DEFAULT_RESERVED_NAMES = ['general']

    def __init__(self, max_length=79, regex=None, reserved_names=None):
        self._max_length = max_length
        regex = regex if regex is not None else self.DEFAULT_REGEX
        self._regex = re.compile(regex) if isinstance(regex, str) else regex

        if reserved_names is not None:
            self._reserved_names = reserved_names
        else:
            self._reserved_names = self.DEFAULT_RESERVED_NAMES

    def __call__(self, value):
        if not value:
            raise ValidationError('Shorter than minimum length 1')
        if len(value) > self._max_length:
            raise ValidationError(f'Longer than maximum length {self._max_length}')
        if value in self._reserved_names:
            raise ValidationError('Reserved Asterisk section name')
        if self._regex.match(value) is None:
            raise ValidationError('Not a valid Asterisk section name')
        return value


class PJSIPSection(AsteriskSection):
    DEFAULT_RESERVED_NAMES = ['global', 'system']
