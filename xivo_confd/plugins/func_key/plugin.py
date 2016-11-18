# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_confd.plugins.func_key.service import build_service, build_user_funckey_template_service
from xivo_confd.plugins.func_key.resource import (FuncKeyTemplateList,
                                                  FuncKeyTemplateItem,
                                                  FuncKeyTemplateItemPosition,
                                                  FuncKeyDestination,
                                                  UserFuncKeyList,
                                                  UserFuncKeyItemPosition,
                                                  UserFuncKeyTemplateAssociation,
                                                  UserFuncKeyTemplateGet,
                                                  FuncKeyTemplateUserGet)

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.func_key_template import dao as template_dao


class Plugin(object):

    def load(self, core):
        api = core.api

        provd_client = core.provd_client()

        service = build_service(provd_client)
        service_association = build_user_funckey_template_service(provd_client)

        # Funckey destination plugin
        api.add_resource(FuncKeyDestination,
                         '/funckeys/destinations',
                         endpoint='func_keys')

        # Funckey Template plugin
        api.add_resource(FuncKeyTemplateList,
                         '/funckeys/templates',
                         resource_class_args=(service,))

        api.add_resource(FuncKeyTemplateItem,
                         '/funckeys/templates/<int:id>',
                         endpoint='func_keys_templates',
                         resource_class_args=(service,))

        api.add_resource(FuncKeyTemplateItemPosition,
                         '/funckeys/templates/<int:id>/<int:position>',
                         resource_class_args=(service,))

        # User-Funckey plugin
        api.add_resource(UserFuncKeyItemPosition,
                         '/users/<uuid:user_id>/funckeys/<int:position>',
                         '/users/<int:user_id>/funckeys/<int:position>',
                         resource_class_args=(service, user_dao, template_dao))

        api.add_resource(UserFuncKeyList,
                         '/users/<uuid:user_id>/funckeys',
                         '/users/<int:user_id>/funckeys',
                         resource_class_args=(service, user_dao, template_dao))

        # User-Funckey Template plugin
        api.add_resource(UserFuncKeyTemplateAssociation,
                         '/users/<uuid:user_id>/funckeys/templates/<int:template_id>',
                         '/users/<int:user_id>/funckeys/templates/<int:template_id>',
                         resource_class_args=(service_association, user_dao, template_dao))

        api.add_resource(UserFuncKeyTemplateGet,
                         '/users/<uuid:user_id>/funckeys/templates',
                         '/users/<int:user_id>/funckeys/templates',
                         resource_class_args=(service_association, user_dao, template_dao))

        api.add_resource(FuncKeyTemplateUserGet,
                         '/funckeys/templates/<int:template_id>/users',
                         resource_class_args=(service_association, user_dao, template_dao))
