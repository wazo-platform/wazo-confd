# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import post_load

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.destination import DestinationField


class UserFallbackSchema(BaseSchema):
    noanswer_destination = DestinationField(attribute='noanswer', default=None, allow_none=True)
    busy_destination = DestinationField(attribute='busy', default=None, allow_none=True)
    congestion_destination = DestinationField(attribute='congestion', default=None, allow_none=True)
    fail_destination = DestinationField(attribute='chanunavail', default=None, allow_none=True)

    @post_load
    def create_objects(self, data):
        for key, form in data.iteritems():
            if form:
                data[key] = Dialaction(**form)
        return data
