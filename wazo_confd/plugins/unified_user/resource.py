# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request
from flask_restful import Resource
import logging

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource as BaseListResource
from xivo.mallow_helpers import handle_validation_exception
from xivo.rest_api_helpers import handle_api_exception

from .schema import UnifiedUserSchema
from .user_schema import UserXivoSchemaNullable
from ..user.resource import UserList as BaseUserList
from ..user.service import UserService
from ..user_import.wazo_user_service import WazoUserService

logger = logging.getLogger(__name__)


class ListResource(BaseListResource):
    method_decorators = [
        handle_validation_exception,
        handle_api_exception,
    ] + Resource.method_decorators


class UserList(BaseUserList):
    schema = UserXivoSchemaNullable

    method_decorators = [
        handle_validation_exception,
        handle_api_exception,
    ] + Resource.method_decorators


class UnifiedUserList(ListResource):
    def __init__(self, user_service: UserService, wazo_user_service: WazoUserService):
        self.user_list_resource = UserList(user_service, json_path='user')
        self.wazo_user_service = wazo_user_service

    def build_headers(self, user):
        return {'Location': url_for('users', id=user['id'], _external=True)}

    @required_acl('confd.unified_users.create')
    def post(self):
        logger.info("Create Unified User")
        UnifiedUserSchema().load(request.get_json())

        logger.info("Create User resource")
        user_dict, _, _ = self.user_list_resource.post()

        logger.info("Create User authentication")
        # FIX: create(...) takes a user dict containing an 'email_address' key, not an 'email' key
        fixed_user_dict = user_dict.copy()
        fixed_user_dict['email_address'] = fixed_user_dict['email']
        self.wazo_user_service.create(fixed_user_dict)

        return (
            {
                'user': user_dict,
            },
            201,
            self.build_headers(user_dict),
        )
