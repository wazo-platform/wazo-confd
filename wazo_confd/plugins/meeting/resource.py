# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import random
import string

from uuid import uuid4

from flask import url_for, request
from requests import HTTPError

from xivo_dao.alchemy.meeting import Meeting
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.helpers import errors

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource, ListSchema

from .schema import MeetingSchema

logger = logging.getLogger(__name__)


class MeetingList(ListResource):

    model = Meeting

    def __init__(
        self,
        service,
        user_service,
        tenant_service,
        endpoint_sip_service,
        endpoint_sip_template_service,
        hostname,
        port,
    ):
        super().__init__(service)
        self._user_service = user_service
        self._tenant_service = tenant_service
        self._endpoint_sip_service = endpoint_sip_service
        self._endpoint_sip_template_service = endpoint_sip_template_service
        self._schema = MeetingSchema()
        self._schema.context = {'hostname': hostname, 'port': port}

    def build_headers(self, meeting):
        return {'Location': url_for('meetings', uuid=meeting.uuid, _external=True)}

    @required_acl('confd.meetings.create')
    def post(self):
        return self._post(request.get_json())

    def _post(self, body):
        form = self.schema().load(body)
        form['uuid'] = uuid4()
        form = self.add_tenant_to_form(form)
        form = self.find_owners(form)
        form = self.add_endpoint_to_form(form)
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.meetings.read')
    def get(self):
        return super().get()

    def schema(self):
        return self._schema

    def add_endpoint_to_form(self, form):
        tenant = self._tenant_service.get(form['tenant_uuid'])
        template_uuid = tenant.meeting_guest_sip_template_uuid
        if not template_uuid:
            logger.warning('Cannot create guest endpoint, missing template')
            return form

        template = self._endpoint_sip_template_service.get(template_uuid)
        endpoint_name = endpoint_username = context = 'wazo-meeting-{}-guest'.format(
            form['uuid']
        )
        endpoint_body = {
            'name': endpoint_name,
            'tenant_uuid': form['tenant_uuid'],
            'label': 'External meeting guest {}'.format(form['name']),
            'templates': [template],
            'auth_section_options': [
                ['username', endpoint_username],
                ['password', random_string(16)],
            ],
            'aor_section_options': [],
            'endpoint_section_options': [
                ['context', context],
            ],
            'identify_section_options': [],
            'registration_section_options': [],
            'registration_outbound_auth_section_options': [],
            'outbound_auth_section_options': [],
        }
        endpoint_model = EndpointSIP(**endpoint_body)
        endpoint = self._endpoint_sip_service.create(endpoint_model)
        form['guest_endpoint_sip_uuid'] = endpoint.uuid
        return form

    def find_owners(self, form):
        owner_uuids = form.pop('owner_uuids', None) or []
        owners = []
        tenant_uuid = form['tenant_uuid']
        for uuid in owner_uuids:
            owners.append(self._user_service.get(uuid, tenant_uuids=[tenant_uuid]))
        form['owners'] = owners
        return form

    def _find_user_uuid(self):
        token = request.headers.get('X-Auth-Token') or request.args.get('token')
        try:
            token_infos = self._auth_client.token.get(token)
        except HTTPError as e:
            logger.warning('HTTP error from wazo-auth while getting token: %s', e)
            raise errors.param_not_found('user_uuid', 'meetings')

        user_uuid = token_infos['metadata']['pbx_user_uuid']
        if not user_uuid:
            raise errors.param_not_found('user_uuid', 'meetings')

        return user_uuid


class MeetingItem(ItemResource):
    has_tenant_uuid = True

    def __init__(self, service, user_service, hostname, port):
        super().__init__(service)
        self._user_service = user_service
        self._schema = MeetingSchema()
        self._schema.context = {'hostname': hostname, 'port': port}

    @required_acl('confd.meetings.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.meetings.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.meetings.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)

    def schema(self):
        return self._schema


class GuestMeetingItem(ItemResource):
    def __init__(self, service, user_service, hostname, port):
        super().__init__(service)
        self._schema = MeetingSchema()
        self._schema.context = {'hostname': hostname, 'port': port}

    def get(self, uuid):
        return super().get(uuid)

    def schema(self):
        return self._schema


class UserMeetingItem(MeetingItem):
    def __init__(self, service, user_service, hostname, port, auth_client):
        super().__init__(service, user_service, hostname, port)
        self._auth_client = auth_client

    def get_model(self, uuid, user_uuid, **kwargs):
        return self.service.get_by(uuid=uuid, owner=user_uuid, **kwargs)

    @required_acl('confd.users.me.meetings.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.users.me.meetings.{uuid}.update')
    def put(self, uuid):
        kwargs = self._add_tenant_uuid()
        kwargs['user_uuid'] = self._find_user_uuid()
        model = self.get_model(uuid, **kwargs)
        self.parse_and_update(model)
        return '', 204

    @required_acl('confd.users.me.meetings.{uuid}.delete')
    def delete(self, uuid):
        kwargs = self._add_tenant_uuid()
        kwargs['user_uuid'] = self._find_user_uuid()
        model = self.get_model(uuid, **kwargs)
        self.service.delete(model)
        return '', 204

    def _find_user_uuid(self):
        token = request.headers.get('X-Auth-Token') or request.args.get('token')
        try:
            token_infos = self._auth_client.token.get(token)
        except HTTPError as e:
            logger.warning('HTTP error from wazo-auth while getting token: %s', e)
            raise errors.param_not_found('user_uuid', 'meetings')

        user_uuid = token_infos['metadata']['pbx_user_uuid']
        if not user_uuid:
            raise errors.param_not_found('user_uuid', 'meetings')

        return user_uuid


class UserMeetingList(MeetingList):

    model = Meeting

    def __init__(
        self,
        service,
        user_service,
        tenant_service,
        endpoint_sip_service,
        endpoint_sip_template_service,
        hostname,
        port,
        auth_client,
    ):
        super().__init__(
            service,
            user_service,
            tenant_service,
            endpoint_sip_service,
            endpoint_sip_template_service,
            hostname,
            port,
        )
        self._auth_client = auth_client

    def build_headers(self, meeting):
        return {'Location': url_for('meetings', uuid=meeting.uuid, _external=True)}

    @required_acl('confd.users.me.meetings.create')
    def post(self):
        body = self.add_user_to_owner_uuids(request.get_json())
        return self._post(body)

    @required_acl('confd.users.me.meetings.read')
    def get(self):
        return super().get()

    def add_user_to_owner_uuids(self, body):
        user_uuid = self._find_user_uuid()
        body['owner_uuids'] = list(set(body.get('owner_uuids', []) + [user_uuid]))
        return body

    def search_params(self):
        params = ListSchema().load(request.args)
        params['owner'] = self._find_user_uuid()
        return params


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
