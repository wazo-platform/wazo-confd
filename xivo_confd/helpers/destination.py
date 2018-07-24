# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import json

from marshmallow import Schema, fields, pre_dump, post_load, post_dump, validates_schema, validates
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, OneOf, Regexp, Predicate, Range

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.conference import dao as meetme_dao
from xivo_dao.resources.conference import dao as conference_dao
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.ivr import dao as ivr_dao
from xivo_dao.resources.outcall import dao as outcall_dao
from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.skill_rule import dao as skill_rule_dao
from xivo_dao.resources.switchboard import dao as switchboard_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao

from xivo_confd.helpers.mallow import StrictBoolean
from xivo_confd.helpers.validator import GetResource, ResourceExists, Validator

COMMAND_REGEX = r'^(?!(try)?system\()[a-zA-Z]{3,}\((.*)\)$'
CONTEXT_REGEX = r'^[a-zA-Z0-9_-]{1,39}$'
EXTEN_REGEX = r'^[0-9*#]{1,255}$'
SKILL_RULE_VARIABLE_REGEX = r'^[^[;\|]+$'


class BaseDestinationSchema(Schema):
    type = fields.String(validate=OneOf(['application',
                                         'conference',
                                         'custom',
                                         'extension',
                                         'group',
                                         'hangup',
                                         'ivr',
                                         'meetme',
                                         'none',
                                         'outcall',
                                         'queue',
                                         'sound',
                                         'switchboard',
                                         'user',
                                         'voicemail']),
                         required=True)

    @post_dump
    def convert_type_to_user(self, data):
        if data['type'] == 'endcall':
            data['type'] = 'hangup'
        return data

    @post_load
    def convert_type_to_database(self, data):
        if data['type'] == 'hangup':
            data['type'] = 'endcall'
        return data


class ApplicationDestinationSchema(BaseDestinationSchema):
    application = fields.String(validate=OneOf(['callback_disa',
                                                'directory',
                                                'disa',
                                                'fax_to_mail',
                                                'voicemail']),
                                attribute='subtype',
                                required=True)

    @post_dump
    def convert_application_to_user(self, data):
        if data['application'] == 'callbackdisa':
            data['application'] = 'callback_disa'
        elif data['application'] == 'faxtomail':
            data['application'] = 'fax_to_mail'
        elif data['application'] == 'voicemailmain':
            data['application'] = 'voicemail'
        return data

    @post_load
    def convert_application_to_database(self, data):
        if data['subtype'] == 'callback_disa':
            data['subtype'] = 'callbackdisa'
        elif data['subtype'] == 'fax_to_mail':
            data['subtype'] = 'faxtomail'
        elif data['subtype'] == 'voicemail':
            data['subtype'] = 'voicemailmain'
        return data


class CallBackDISADestinationSchema(ApplicationDestinationSchema):
    pin = fields.String(validate=(Predicate('isdigit'), Length(max=40)),
                        allow_none=True,
                        attribute='actionarg1')

    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg2', required=True)


class DISADestinationSchema(ApplicationDestinationSchema):
    pin = fields.String(validate=(Predicate('isdigit'), Length(max=40)),
                        allow_none=True,
                        attribute='actionarg1')
    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg2', required=True)


class DirectoryDestinationSchema(ApplicationDestinationSchema):
    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg1', required=True)


class FaxToMailDestinationSchema(ApplicationDestinationSchema):
    email = fields.Email(validate=Length(max=80), attribute='actionarg1', required=True)


class VoicemailMainDestinationSchema(ApplicationDestinationSchema):
    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg1', required=True)


class MeetmeDestinationSchema(BaseDestinationSchema):
    conference_id = fields.Integer(attribute='actionarg1', required=True)


class ConferenceDestinationSchema(BaseDestinationSchema):
    conference_id = fields.Integer(attribute='actionarg1', required=True)

    conference = fields.Nested('ConferenceSchema',
                               only=['name'],
                               dump_only=True)

    @post_dump
    def make_conference_fields_flat(self, data):
        if data.get('conference'):
            data['conference_name'] = data['conference']['name']

        data.pop('conference', None)
        return data


class CustomDestinationSchema(BaseDestinationSchema):
    command = fields.String(validate=(Regexp(COMMAND_REGEX), Length(max=255)),
                            attribute='actionarg1', required=True)


class ExtensionDestinationSchema(BaseDestinationSchema):
    exten = fields.String(validate=Regexp(CONTEXT_REGEX),
                          attribute='actionarg1', required=True)
    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg2', required=True)


class GroupDestinationSchema(BaseDestinationSchema):
    group_id = fields.Integer(attribute='actionarg1', required=True)
    ring_time = fields.Float(validate=Range(min=0), attribute='actionarg2', allow_none=True)

    group = fields.Nested('GroupSchema',
                          only=['name'],
                          dump_only=True)

    @post_dump
    def make_group_fields_flat(self, data):
        if data.get('group'):
            data['group_name'] = data['group']['name']

        data.pop('group', None)
        return data


class HangupDestinationSchema(BaseDestinationSchema):
    cause = fields.String(validate=OneOf(['busy',
                                          'congestion',
                                          'normal']),
                          attribute='subtype',
                          missing='normal',
                          required=True)

    @post_dump
    def convert_cause_to_user(self, data):
        if data['cause'] == 'hangup':
            data['cause'] = 'normal'
        return data

    @post_load
    def convert_cause_to_database(self, data):
        if data['subtype'] == 'normal':
            data['subtype'] = 'hangup'
        return data


class BusyDestinationSchema(HangupDestinationSchema):
    timeout = fields.Float(attribute='actionarg1', validate=Range(min=0), allow_none=True)


class CongestionDestinationSchema(HangupDestinationSchema):
    timeout = fields.Float(attribute='actionarg1', validate=Range(min=0), allow_none=True)


class IVRDestinationSchema(BaseDestinationSchema):
    ivr_id = fields.Integer(attribute='actionarg1', required=True)

    ivr = fields.Nested('IvrSchema',
                        only=['name'],
                        dump_only=True)

    @post_dump
    def make_ivr_fields_flat(self, data):
        if data.get('ivr'):
            data['ivr_name'] = data['ivr']['name']

        data.pop('ivr', None)
        return data


class NormalDestinationSchema(HangupDestinationSchema):
    pass


class NoneDestinationSchema(BaseDestinationSchema):
    pass


class OutcallDestinationSchema(BaseDestinationSchema):
    outcall_id = fields.Integer(attribute='actionarg1', required=True)
    exten = fields.String(validate=(Predicate('isdigit'), Length(max=255)),
                          attribute='actionarg2',
                          required=True)


class QueueDestinationSchema(BaseDestinationSchema):
    queue_id = fields.Integer(attribute='actionarg1', required=True)
    ring_time = fields.Float(validate=Range(min=0), allow_none=True)
    skill_rule_id = fields.Integer(allow_none=True)
    skill_rule_variables = fields.Dict(allow_none=True)

    @pre_dump
    def separate_action(self, data):
        options = data.actionarg2.split(';') if data.actionarg2 else []
        data.ring_time = None
        data.skill_rule_id = None
        _skill_rule_variables = None
        if len(options) == 1:
            data.ring_time = options[0] or None
        elif len(options) == 2:  # id is always bound with variables
            data.skill_rule_id = options[0]
            _skill_rule_variables = options[1] or None
        elif len(options) == 3:
            data.ring_time = options[0]
            data.skill_rule_id = options[1]
            _skill_rule_variables = options[2] or None

        if _skill_rule_variables:
            _skill_rule_variables = _skill_rule_variables.replace('|', ',')  # dialplan interpret comma ...
            data.skill_rule_variables = json.loads(_skill_rule_variables)
        return data

    @post_load
    def merge_action(self, data):
        ring_time = data.pop('ring_time', None)
        skill_rule_id = data.pop('skill_rule_id', None)
        skill_rule_variables = data.pop('skill_rule_variables', None)
        skill_rule_variables_str = json.dumps(skill_rule_variables).replace(',', '|') if skill_rule_variables else ''
        data['actionarg2'] = '{ring_time}{sep1}{skill_rule_id}{sep2}{skill_rule_variables}'.format(
            ring_time=ring_time or '',
            sep1=';' if ring_time and skill_rule_id else '',
            skill_rule_id=skill_rule_id or '',
            sep2=';' if skill_rule_id else '',
            skill_rule_variables=skill_rule_variables_str,
        )
        return data

    @validates_schema
    def _validate_skill_rule_variables(self, data):
        if not data.get('skill_rule_variables'):
            return
        if not data.get('skill_rule_id'):
            raise ValidationError(
                'Missing data for required field. When `skill_rule_variables` is defined',
                ['skill_rule_id']
            )

    @validates('skill_rule_variables')
    def _validate_skill_rule_variables_value(self, variables):
        # with marshmallow 3.0 we can set this validator on the field declaration
        if not variables:
            return

        validator = Regexp(SKILL_RULE_VARIABLE_REGEX)
        for key, value in variables.items():
            validator(key)
            validator(value)


class SoundDestinationSchema(BaseDestinationSchema):
    filename = fields.String(validate=Length(max=255), attribute='actionarg1', required=True)
    skip = StrictBoolean()
    no_answer = StrictBoolean()

    @pre_dump
    def separate_action(self, data):
        options = data.actionarg2 if data.actionarg2 else ''
        data.skip = True if 'skip' in options else False
        data.no_answer = True if 'noanswer' in options else False
        return data

    @post_load
    def merge_action(self, data):
        data['actionarg2'] = '{skip}{noanswer}'.format(
            skip='skip' if data.pop('skip', False) else '',
            noanswer='noanswer' if data.pop('no_answer', False) else ''
        )
        return data


class SwitchboardDestinationSchema(BaseDestinationSchema):
    switchboard_uuid = fields.UUID(attribute='actionarg1', required=True)
    ring_time = fields.Float(validate=Range(min=0), attribute='actionarg2', allow_none=True)

    switchboard = fields.Nested('SwitchboardSchema',
                                only=['name'],
                                dump_only=True)

    @post_dump
    def make_switchboard_fields_flat(self, data):
        if data.get('switchboard'):
            data['switchboard_name'] = data['switchboard']['name']

        data.pop('switchboard', None)
        return data


class UserDestinationSchema(BaseDestinationSchema):
    user_id = fields.Integer(attribute='actionarg1', required=True)
    ring_time = fields.Float(validate=Range(min=0), attribute='actionarg2', allow_none=True)

    user = fields.Nested('UserSchema',
                         only=['firstname',
                               'lastname'],
                         dump_only=True)

    @post_dump
    def make_user_fields_flat(self, data):
        if data.get('user'):
            data['user_firstname'] = data['user']['firstname']
            data['user_lastname'] = data['user']['lastname']

        data.pop('user', None)
        return data


class VoicemailDestinationSchema(BaseDestinationSchema):
    voicemail_id = fields.Integer(attribute='actionarg1', required=True)
    skip_instructions = StrictBoolean()
    greeting = fields.String(validate=OneOf(['busy', 'unavailable']), allow_none=True)

    voicemail = fields.Nested('VoicemailSchema',
                              only=['name'],
                              dump_only=True)

    @pre_dump
    def separate_action(self, data):
        options = data.actionarg2 if data.actionarg2 else ''
        data.skip_instructions = True if 's' in options else False
        data.greeting = 'busy' if 'b' in options else 'unavailable' if 'u' in options else None
        return data

    @post_load
    def merge_action(self, data):
        greeting = data.pop('greeting', None)
        data['actionarg2'] = '{}{}'.format(
            'b' if greeting == 'busy' else 'u' if greeting == 'unavailable' else '',
            's' if data.pop('skip_instructions', False) else ''
        )
        return data

    @post_dump
    def make_voicemail_fields_flat(self, data):
        if data.get('voicemail'):
            data['voicemail_name'] = data['voicemail']['name']

        data.pop('voicemail', None)
        return data


class DestinationField(fields.Nested):

    application_schemas = {
        'callback_disa': CallBackDISADestinationSchema,
        'callbackdisa': CallBackDISADestinationSchema,
        'directory': DirectoryDestinationSchema,
        'disa': DISADestinationSchema,
        'fax_to_mail': FaxToMailDestinationSchema,
        'faxtomail': FaxToMailDestinationSchema,
        'voicemail': VoicemailMainDestinationSchema,
        'voicemailmain': VoicemailMainDestinationSchema,
    }

    hangup_schemas = {
        'busy': BusyDestinationSchema,
        'congestion': CongestionDestinationSchema,
        'normal': NormalDestinationSchema,
        'hangup': NormalDestinationSchema,
    }

    destination_schemas = {
        'application': ApplicationDestinationSchema,
        'conference': ConferenceDestinationSchema,
        'custom': CustomDestinationSchema,
        'extension': ExtensionDestinationSchema,
        'group': GroupDestinationSchema,
        'hangup': HangupDestinationSchema,
        'endcall': HangupDestinationSchema,
        'ivr': IVRDestinationSchema,
        'meetme': MeetmeDestinationSchema,
        'none': NoneDestinationSchema,
        'outcall': OutcallDestinationSchema,
        'queue': QueueDestinationSchema,
        'sound': SoundDestinationSchema,
        'switchboard': SwitchboardDestinationSchema,
        'user': UserDestinationSchema,
        'voicemail': VoicemailDestinationSchema,
    }

    def __init__(self, **kwargs):
        super(DestinationField, self).__init__(BaseDestinationSchema, **kwargs)

    def _deserialize(self, value, attr, data):
        self.schema.context = self.context
        base = super(DestinationField, self)._deserialize(value, attr, data)
        schema = self.destination_schemas[base['type']]

        if base['type'] == 'application':
            base = fields.Nested(schema)._deserialize(value, attr, data)
            schema = self.application_schemas[base['subtype']]

        if base['type'] == 'endcall':
            base = fields.Nested(schema)._deserialize(value, attr, data)
            schema = self.hangup_schemas[base['subtype']]

        return fields.Nested(schema)._deserialize(value, attr, data)

    def _serialize(self, nested_obj, attr, obj):
        base = super(DestinationField, self)._serialize(nested_obj, attr, obj)
        if not base:
            return base
        schema = self.destination_schemas[base['type']]

        if base['type'] == 'application':
            base = fields.Nested(schema)._serialize(nested_obj, attr, obj)
            schema = self.application_schemas[base['application']]

        if base['type'] == 'hangup':
            base = fields.Nested(schema)._serialize(nested_obj, attr, obj)
            schema = self.hangup_schemas[base['cause']]

        return fields.Nested(schema)._serialize(nested_obj, attr, obj)


class OptionalGetSkillRuleFromActionArg2Resource(Validator):

    def __init__(self, dao_get):
        self.dao_get = dao_get

    def validate(self, model):
        destination, _ = QueueDestinationSchema().dump(model)
        skill_rule_id = destination.get('skill_rule_id', None)
        if not skill_rule_id:
            return
        try:
            self.dao_get(skill_rule_id)
        except NotFoundError:
            metadata = {'skill_rule_id': skill_rule_id}
            raise errors.param_not_found('skill_rule_id', 'SkillRule', **metadata)


class DestinationValidator(object):

    _VALIDATORS = {
        'application:callbackdisa': [],
        'application:directory': [],
        'application:disa': [],
        'application:faxtomail': [],
        'application:voicemailmain': [],
        'conference': [GetResource('actionarg1', conference_dao.get, 'Conference')],
        'custom': [],
        'extension': [],
        'group': [GetResource('actionarg1', group_dao.get, 'Group')],
        'endcall:busy': [],
        'endcall:congestion': [],
        'endcall:hangup': [],
        'ivr': [GetResource('actionarg1', ivr_dao.get, 'IVR')],
        'meetme': [ResourceExists('actionarg1', meetme_dao.exists, 'Conference')],
        'none': [],
        'outcall': [GetResource('actionarg1', outcall_dao.get, 'Outcall')],
        'queue': [
            GetResource('actionarg1', queue_dao.get, 'Queue'),
            OptionalGetSkillRuleFromActionArg2Resource(skill_rule_dao.get),
        ],
        'sound': [],
        'switchboard': [GetResource('actionarg1', switchboard_dao.get, 'Switchboard')],
        'user': [GetResource('actionarg1', user_dao.get, 'User')],
        'voicemail': [GetResource('actionarg1', voicemail_dao.get, 'Voicemail')],
    }

    def validate(self, destination):
        for validator in self._VALIDATORS[destination.action]:
            validator.validate(destination)
