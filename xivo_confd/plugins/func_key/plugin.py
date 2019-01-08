# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.func_key_template import dao as template_dao
from wazo_provd_client import Client as ProvdClient

from .resource import (
    FuncKeyTemplateList,
    FuncKeyTemplateItem,
    FuncKeyTemplateItemPosition,
    FuncKeyDestination,
    UserFuncKeyList,
    UserFuncKeyItemPosition,
    UserFuncKeyTemplateAssociation,
    UserFuncKeyTemplateGet,
    FuncKeyTemplateUserGet
)
from .service import build_service, build_user_funckey_template_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(provd_client)
        service_association = build_user_funckey_template_service(provd_client)

        # Funckey destination plugin
        api.add_resource(
            FuncKeyDestination,
            '/funckeys/destinations',
            endpoint='func_keys'
        )

        # Funckey Template plugin
        api.add_resource(
            FuncKeyTemplateList,
            '/funckeys/templates',
            resource_class_args=(service,)
        )

        api.add_resource(
            FuncKeyTemplateItem,
            '/funckeys/templates/<int:id>',
            endpoint='func_keys_templates',
            resource_class_args=(service,)
        )

        api.add_resource(
            FuncKeyTemplateItemPosition,
            '/funckeys/templates/<int:id>/<int:position>',
            resource_class_args=(service,)
        )

        # User-Funckey plugin
        api.add_resource(
            UserFuncKeyItemPosition,
            '/users/<uuid:user_id>/funckeys/<int:position>',
            '/users/<int:user_id>/funckeys/<int:position>',
            resource_class_args=(service, user_dao, template_dao)
        )

        api.add_resource(
            UserFuncKeyList,
            '/users/<uuid:user_id>/funckeys',
            '/users/<int:user_id>/funckeys',
            resource_class_args=(service, user_dao, template_dao)
        )

        # User-Funckey Template plugin
        api.add_resource(
            UserFuncKeyTemplateAssociation,
            '/users/<uuid:user_id>/funckeys/templates/<int:template_id>',
            '/users/<int:user_id>/funckeys/templates/<int:template_id>',
            resource_class_args=(service_association, user_dao, template_dao)
        )

        api.add_resource(
            UserFuncKeyTemplateGet,
            '/users/<uuid:user_id>/funckeys/templates',
            '/users/<int:user_id>/funckeys/templates',
            resource_class_args=(service_association, user_dao, template_dao)
        )

        api.add_resource(
            FuncKeyTemplateUserGet,
            '/funckeys/templates/<int:template_id>/users',
            resource_class_args=(service_association, user_dao, template_dao)
        )
