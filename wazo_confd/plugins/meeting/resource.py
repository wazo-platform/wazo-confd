# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import secrets
import string

from uuid import uuid4

from flask import url_for, request

from wazo.xivo_helpers import clean_extension
from wazo.tenant_flask_helpers import user

from xivo_dao.alchemy.meeting import Meeting
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.helpers import errors

from wazo_confd.auth import required_acl, no_auth, master_tenant_uuid
from wazo_confd.helpers.restful import ItemResource, ListResource, ListSchema

from .exceptions import MeetingGuestSIPTemplateNotFound
from .schema import MeetingSchema

logger = logging.getLogger(__name__)


class _SchemaMixin:
    def _init_schema(self):
        self._schema = MeetingSchema()

    def schema(self):
        ingress_http = self._ingress_http_service.find_by(
            tenant_uuid=str(master_tenant_uuid)
        )
        exten_pattern = None
        exten_prefix = None
        extens = self._extension_features_service.search(
            {'feature': 'meetingjoin'}
        ).items
        for exten in extens:
            if exten.feature == 'meetingjoin' and exten.enabled:
                exten_pattern = exten.exten
                break
        if exten_pattern:
            exten_prefix = clean_extension(exten_pattern)

        self._schema.context = {
            'default_ingress_http': ingress_http,
            'exten_prefix': exten_prefix,
        }
        return self._schema


class _MeResourceMixin:
    def _find_user_uuid(self):
        if not user.uuid:
            raise errors.param_not_found('user_uuid', 'meetings')

        return user.uuid


def find_owners(form, tenant_uuid, user_service):
    owner_uuids = form.pop('owner_uuids', None) or []
    owners = [
        user_service.get(uuid, tenant_uuids=[tenant_uuid]) for uuid in owner_uuids
    ]
    form['owners'] = owners
    return form


class MeetingList(ListResource, _SchemaMixin, _MeResourceMixin):
    model = Meeting

    def __init__(
        self,
        service,
        user_service,
        tenant_service,
        endpoint_sip_service,
        endpoint_sip_template_service,
        ingress_http_service,
        extension_features_service,
    ):
        super().__init__(service)
        self._user_service = user_service
        self._tenant_service = tenant_service
        self._endpoint_sip_service = endpoint_sip_service
        self._endpoint_sip_template_service = endpoint_sip_template_service
        self._ingress_http_service = ingress_http_service
        self._extension_features_service = extension_features_service
        self._init_schema()

    def build_headers(self, meeting):
        return {'Location': url_for('meetings', uuid=meeting.uuid, _external=True)}

    @required_acl('confd.meetings.create')
    def post(self):
        return self._post(request.get_json())

    def _post(self, body):
        form = self.schema().load(body)
        form['uuid'] = uuid4()
        form = self.add_tenant_to_form(form)
        form = find_owners(form, form['tenant_uuid'], self._user_service)
        form = self.add_endpoint_to_form(form)
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.meetings.read')
    def get(self):
        return super().get()

    def add_endpoint_to_form(self, form):
        tenant = self._tenant_service.get(form['tenant_uuid'])
        template_uuid = tenant.meeting_guest_sip_template_uuid
        if not template_uuid:
            raise MeetingGuestSIPTemplateNotFound(form['tenant_uuid'])

        template = self._endpoint_sip_template_service.get(template_uuid)
        context = 'wazo-meeting-guest'
        endpoint_name = endpoint_username = 'wazo-meeting-{}-guest'.format(form['uuid'])
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


class MeetingItem(ItemResource, _SchemaMixin):
    has_tenant_uuid = True

    def __init__(
        self, service, user_service, ingress_http_service, extension_features_service
    ):
        super().__init__(service)
        self._user_service = user_service
        self._ingress_http_service = ingress_http_service
        self._extension_features_service = extension_features_service
        self._init_schema()

    @required_acl('confd.meetings.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.meetings.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    def parse_and_update(self, model, **kwargs):
        form = self.schema().load(request.get_json(), partial=True)
        form = find_owners(form, model.tenant_uuid, self._user_service)
        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.items():
            setattr(model, name, value)
        self.service.edit(model, updated_fields=updated_fields, **kwargs)

    @required_acl('confd.meetings.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)


class GuestMeetingItem(ItemResource, _SchemaMixin):
    def __init__(
        self, service, user_service, ingress_http_service, extension_features_service
    ):
        super().__init__(service)
        self._ingress_http_service = ingress_http_service
        self._extension_features_service = extension_features_service
        self._init_schema()

    @no_auth
    def get(self, uuid):
        return super().get(uuid)


class UserMeetingItem(MeetingItem, _MeResourceMixin):
    def __init__(
        self,
        service,
        user_service,
        ingress_http_service,
        extension_features_service,
        auth_client,
    ):
        super().__init__(
            service, user_service, ingress_http_service, extension_features_service
        )
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
        self.parse_and_update(model, **kwargs)
        return '', 204

    def parse_and_update(self, model, **kwargs):
        form = self.schema().load(request.get_json(), partial=True)

        if not self._current_user_in_owners(kwargs['user_uuid'], form):
            self._add_current_user_owner(kwargs['user_uuid'], form)
        form = find_owners(form, model.tenant_uuid, self._user_service)

        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.items():
            setattr(model, name, value)
        self.service.edit(model, updated_fields=updated_fields)

    @staticmethod
    def _current_user_in_owners(user_uuid, form):
        return user_uuid in form['owner_uuids']

    @staticmethod
    def _add_current_user_owner(user_uuid, form):
        return form['owner_uuids'].append(user_uuid)

    @required_acl('confd.users.me.meetings.{uuid}.delete')
    def delete(self, uuid):
        kwargs = self._add_tenant_uuid()
        kwargs['user_uuid'] = self._find_user_uuid()
        model = self.get_model(uuid, **kwargs)
        self.service.delete(model)
        return '', 204


class UserMeetingList(MeetingList):
    model = Meeting

    def __init__(
        self,
        service,
        user_service,
        tenant_service,
        endpoint_sip_service,
        endpoint_sip_template_service,
        ingress_http_service,
        extension_features_service,
        auth_client,
    ):
        super().__init__(
            service,
            user_service,
            tenant_service,
            endpoint_sip_service,
            endpoint_sip_template_service,
            ingress_http_service,
            extension_features_service,
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
    return ''.join(secrets.choice(string.ascii_lowercase) for _ in range(length))
