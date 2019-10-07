# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import post_load

from xivo_dao.alchemy.dialaction import Dialaction
from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.destination import DestinationField


class GroupFallbackSchema(BaseSchema):
    noanswer_destination = DestinationField(
        attribute='noanswer', default=None, allow_none=True
    )

    @post_load
    def create_objects(self, data):
        for key, form in data.items():
            if form:
                data[key] = Dialaction(**form)
        return data
