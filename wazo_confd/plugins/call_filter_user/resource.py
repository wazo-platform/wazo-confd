# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from xivo_dao.alchemy.callfiltermember import Callfiltermember as CallFilterMember
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource

from .schema import CallFilterRecipientUsersSchema, CallFilterSurrogateUsersSchema


class CallFilterRecipientUserList(ConfdResource):

    schema = CallFilterRecipientUsersSchema
    has_tenant_uuid = True

    def __init__(self, service, call_filter_dao, user_dao):
        self.service = service
        self.call_filter_dao = call_filter_dao
        self.user_dao = user_dao

    @required_acl('confd.callfilters.{call_filter_id}.recipients.users.update')
    def put(self, call_filter_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        call_filter = self.call_filter_dao.get(
            call_filter_id, tenant_uuids=tenant_uuids
        )
        form = self.schema().load(request.get_json())
        try:
            recipients = []
            for user_form in form['users']:
                user = self.user_dao.get_by(
                    uuid=user_form['user']['uuid'], tenant_uuids=tenant_uuids
                )
                recipient = self.service.find_recipient_by_user(call_filter, user)
                if not recipient:
                    recipient = CallFilterMember()
                    recipient.user = user
                recipient.timeout = user_form['timeout']
                recipients.append(recipient)

        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_recipients(call_filter, recipients)
        return '', 204


class CallFilterSurrogateUserList(ConfdResource):

    schema = CallFilterSurrogateUsersSchema
    has_tenant_uuid = True

    def __init__(self, service, call_filter_dao, user_dao):
        self.service = service
        self.call_filter_dao = call_filter_dao
        self.user_dao = user_dao

    @required_acl('confd.callfilters.{call_filter_id}.surrogates.users.update')
    def put(self, call_filter_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        call_filter = self.call_filter_dao.get(
            call_filter_id, tenant_uuids=tenant_uuids
        )
        form = self.schema().load(request.get_json())
        try:
            surrogates = []
            for user_form in form['users']:
                user = self.user_dao.get_by(
                    uuid=user_form['user']['uuid'], tenant_uuids=tenant_uuids
                )
                surrogate = self.service.find_surrogate_by_user(call_filter, user)
                if not surrogate:
                    surrogate = CallFilterMember()
                    surrogate.user = user
                surrogates.append(surrogate)

        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_surrogates(call_filter, surrogates)
        return '', 204
