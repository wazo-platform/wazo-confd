# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from flask import Response

from marshmallow import fields, validates_schema

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource
from xivo_dao.helpers import errors


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

        mapped_call_logs = map(self.mapper.to_api, call_logs)
        response = self.serializer.encode_list(mapped_call_logs)
        return Response(response=response,
                        status=200,
                        headers={'Content-disposition': 'attachment;filename=xivo-call-logs.csv'},
                        content_type='text/csv; charset=utf-8')
