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
from .user_schema import UserSchemaNullable
from ..user.resource import UserList as BaseUserList

logger = logging.getLogger(__name__)


class ListResource(BaseListResource):
    method_decorators = [
                            handle_validation_exception,
                            handle_api_exception,
                        ] + Resource.method_decorators


class UserList(BaseUserList):
    schema = UserSchemaNullable

    method_decorators = [
                            handle_validation_exception,
                            handle_api_exception,
                        ] + Resource.method_decorators


class UnifiedUserList(ListResource):

    def __init__(self, user_service):
        self.user_list_resource = UserList(user_service, json_path='user')

    def build_headers(self, user):
        return {'Location': url_for('users', id=user['id'], _external=True)}

    @required_acl('confd.unified_users.create')
    def post(self):
        logger.info("Create Unified User")
        UnifiedUserSchema().load(request.get_json())

        logger.info("Create User resource")
        user_dict, _, _ = self.user_list_resource.post()

        return {'user': user_dict, }, 201, self.build_headers(user_dict)
