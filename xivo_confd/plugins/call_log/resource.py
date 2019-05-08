# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, Response
from marshmallow import fields, validates_schema

from xivo_dao.helpers import errors

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource


class PeriodSchema(BaseSchema):
    start_date = fields.DateTime()
    end_date = fields.DateTime()

    dateformat = 'iso'

    @validates_schema()
    def validate_dates(self, data):
        if not data.get('start_date') and not data.get('end_date'):
            return
        if not data.get('start_date'):
            raise errors.missing('start_date')
        if not data.get('end_date'):
            raise errors.missing('end_date')


class CallLog(ConfdResource):

    schema = PeriodSchema

    def __init__(self, service, serializer, mapper):
        super(CallLog, self).__init__()
        self.service = service
        self.serializer = serializer
        self.mapper = mapper

    @required_acl('confd.call_logs.read')
    def get(self):
        period = self.schema().load(request.args).data
        if not period:
            call_logs = self.service.find_all()
        else:
            call_logs = self.service.find_all_in_period(period['start_date'], period['end_date'])

        mapped_call_logs = list(map(self.mapper.to_api, call_logs))
        response = self.serializer.encode_list(mapped_call_logs)
        return Response(response=response,
                        status=200,
                        headers={'Content-disposition': 'attachment;filename=xivo-call-logs.csv'},
                        content_type='text/csv; charset=utf-8')
