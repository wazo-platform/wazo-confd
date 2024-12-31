# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import post_load

from xivo_dao.alchemy.dialaction import Dialaction
from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.destination import DestinationField


class UserFallbackSchema(BaseSchema):
    noanswer_destination = DestinationField(
        attribute='noanswer', dump_default=None, allow_none=True
    )
    busy_destination = DestinationField(
        attribute='busy', dump_default=None, allow_none=True
    )
    congestion_destination = DestinationField(
        attribute='congestion', dump_default=None, allow_none=True
    )
    fail_destination = DestinationField(
        attribute='chanunavail', dump_default=None, allow_none=True
    )

    @post_load
    def create_objects(self, data, **kwargs):
        for key, form in data.items():
            if form:
                data[key] = Dialaction(**form)
        return data
