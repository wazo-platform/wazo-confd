# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, validates, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, Regexp, Range

from xivo_dao.alchemy.schedule_time import ScheduleTime
from xivo_confd.helpers.destination import DestinationField
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


HOUR_REGEX = r"^([0,1][0-9]|2[0-3]):[0-5][0-9]$"


class ScheduleOpenPeriod(BaseSchema):
    hours_start = fields.String(validate=Regexp(HOUR_REGEX), required=True)
    hours_end = fields.String(validate=Regexp(HOUR_REGEX), required=True)
    week_days = fields.List(
        fields.Integer(validate=Range(min=1, max=7)),
        missing=[1, 2, 3, 4, 5, 6, 7]
    )
    month_days = fields.List(
        fields.Integer(validate=Range(min=1, max=31)),
        missing=[1, 2, 3, 4, 5, 6, 7, 8, 9,
                 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                 30, 31]
    )
    months = fields.List(
        fields.Integer(validate=Range(min=1, max=12)),
        attribute='months_list',
        missing=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    )

    @validates_schema
    def validate_hours(self, data):
        if not data.get('hours_start') or not data.get('hours_end'):
            return

        start_hour, start_min = map(int, data['hours_start'].split(':', 1))
        end_hour, end_min = map(int, data['hours_end'].split(':', 1))
        if (start_hour, start_min) > (end_hour, end_min):
            raise ValidationError('hours_end is before hours_start')

    @validates('week_days')
    def validate_week_days_length(self, value):
        if len(value) < 1:
            raise ValidationError('week_days cannot be empty')

    @validates('month_days')
    def validate_month_days_length(self, value):
        if len(value) < 1:
            raise ValidationError('month_days cannot be empty')

    @validates('months')
    def validate_months_length(self, value):
        if len(value) < 1:
            raise ValidationError('months cannot be empty')

    @post_load
    def create_object(self, data):
        return ScheduleTime(**data)


class ScheduleExceptionalPeriod(ScheduleOpenPeriod):
    destination = DestinationField(required=True)

    @post_load
    def create_object(self, data):
        if 'destination' in data:
            data['type'] = data['destination'].get('type')
            data['subtype'] = data['destination'].get('subtype')
            data['actionarg1'] = data['destination'].get('actionarg1')
            data['actionarg2'] = data['destination'].get('actionarg2')
            data.pop('destination')
        return ScheduleTime(**data)


class ScheduleSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), allow_none=True)
    timezone = fields.String(validate=Length(max=128), allow_none=True)
    closed_destination = DestinationField(required=True)
    open_periods = fields.Nested('ScheduleOpenPeriod', many=True)
    exceptional_periods = fields.Nested('ScheduleExceptionalPeriod', many=True)

    enabled = fields.Boolean()
    links = ListLink(Link('schedules'))

    incalls = fields.Nested('IncallSchema',
                            only=['id', 'links'],
                            many=True,
                            dump_only=True)
    users = fields.Nested('UserSchema',
                          only=['uuid', 'firstname', 'lastname', 'links'],
                          many=True,
                          dump_only=True)
    groups = fields.Nested('GroupSchema',
                           only=['id', 'name', 'links'],
                           many=True,
                           dump_only=True)
    queues = fields.Nested('QueueSchema',
                           only=['id', 'name', 'label', 'links'],
                           many=True,
                           dump_only=True)
    outcalls = fields.Nested('OutcallSchema',
                             only=['id', 'name', 'links'],
                             many=True,
                             dump_only=True)

    @post_load
    def unwrap_closed_destination(self, data):
        if 'closed_destination' in data:
            data['type'] = data['closed_destination'].get('type')
            data['subtype'] = data['closed_destination'].get('subtype')
            data['actionarg1'] = data['closed_destination'].get('actionarg1')
            data['actionarg2'] = data['closed_destination'].get('actionarg2')
            data.pop('closed_destination')
        return data
