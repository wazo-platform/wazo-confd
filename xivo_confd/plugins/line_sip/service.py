# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.plugins.line_sip.model import LineSip

from xivo_confd.plugins.line.service import build_service as build_line_service
from xivo_confd.plugins.endpoint_sip.service import build_service as build_sip_service


class LineSipService(object):

    def __init__(self, line_service, sip_service):
        self.line_service = line_service
        self.sip_service = sip_service

    def get(self, id):
        line = self.line_service.get(id)
        if line.endpoint_sip is None:
            raise errors.not_found('LineSIP', id=id)
        return LineSip.from_line_and_sip(line, line.endpoint_sip)

    def search(self, params):
        total, items = self.line_service.search(params)
        items = (LineSip.from_line_and_sip(line, line.endpoint_sip)
                 for line in items
                 if line.endpoint_sip is not None)
        return total, items

    def create(self, line_sip):
        sip = self.create_sip(line_sip)
        line = self.create_line(line_sip, sip)
        return LineSip.from_line_and_sip(line, sip)

    def create_sip(self, line_sip):
        sip = line_sip.build_sip()
        created_sip = self.sip_service.create(sip)
        return created_sip

    def create_line(self, line_sip, sip):
        line = line_sip.build_line(sip)
        return self.line_service.create(line, None)

    def edit(self, line_sip, updated_fields=[]):
        line = self.line_service.get(line_sip.id)
        sip = self.sip_service.get(line.protocolid)

        line_sip.update_sip(sip)
        self.sip_service.edit(sip)

        line_sip.update_line(line)
        self.line_service.edit(line, None)

    def delete(self, line_sip):
        line = self.line_service.get(line_sip.id)
        sip = self.sip_service.get(line.protocolid)
        self.line_service.delete(line)
        self.sip_service.delete(sip)


def build_service(provd_client):
    return LineSipService(build_line_service(provd_client),
                          build_sip_service(provd_client))
