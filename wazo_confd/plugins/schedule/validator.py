# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_dump, pre_dump, post_load
from marshmallow.validate import Range

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.moh import dao as moh_dao

from wazo_confd.helpers.validator import GetResource, Validator, ValidationGroup
from wazo_confd.helpers.destination import BaseDestinationSchema


# This is a copy of the destination helper, only difference being the name of the columns
class UserDestinationSchema(BaseDestinationSchema):
    user_id = fields.Integer(attribute='fallback_actionid', required=True)
    ring_time = fields.Float(validate=Range(min=0), allow_none=True)
    moh_uuid = fields.UUID(allow_none=True)

    user = fields.Nested('UserSchema', only=['firstname', 'lastname'], dump_only=True)

    @post_dump
    def make_user_fields_flat(self, data):
        if data.get('user'):
            data['user_firstname'] = data['user']['firstname']
            data['user_lastname'] = data['user']['lastname']

        data.pop('user', None)
        return data

    @pre_dump
    def separate_action(self, data):
        options = (
            data.fallback_actionargs.split(';') if data.fallback_actionargs else []
        )
        data.ring_time = None
        data.moh_uuid = None

        if len(options) > 0:
            data.ring_time = options[0] or None

        if len(options) > 1:  # id is always bound with variables
            data.moh_uuid = options[1]

        return data

    @post_load
    def merge_action(self, data):
        ring_time = data.pop('ring_time', None)
        moh_uuid = data.pop('moh_uuid', None)

        fallback_actionargs = ''
        if ring_time is not None:
            fallback_actionargs += str(ring_time)
        if moh_uuid is not None:
            fallback_actionargs += ';{}'.format(moh_uuid)

        data['fallback_actionargs'] = fallback_actionargs
        return data


class GetMohFromClosedSchedule(Validator):
    def __init__(self, dao_get):
        self._dao_get = dao_get

    def validate(self, model):
        destination = UserDestinationSchema().dump(model)
        moh_uuid = destination.get('moh_uuid', None)
        if not moh_uuid:
            return

        try:
            self._dao_get(moh_uuid)
        except NotFoundError:
            metadata = {'moh_uuid': moh_uuid}
            raise errors.param_not_found('moh_uuid', 'MOH', **metadata)


# This is a copy of the Destination validator with the difference that not all resources are
# validated and the fields are not the same as the dialaction table
class ClosedDestinationValidator:

    _VALIDATORS = {
        'user': [
            GetResource('fallback_actionid', user_dao.get, 'User'),
            GetMohFromClosedSchedule(moh_dao.get),
        ],
    }

    def validate(self, schedule):
        for validator in self._VALIDATORS.get(schedule.fallback_action, []):
            validator.validate(schedule)


class ScheduleModelValidator(Validator):
    def __init__(self, destination_validator):
        self._destination_validator = destination_validator

    def validate(self, schedule):
        self._destination_validator.validate(schedule.closed_destination)


def build_validator():
    schedule_validator = ScheduleModelValidator(ClosedDestinationValidator())
    return ValidationGroup(create=[schedule_validator], edit=[schedule_validator])
