# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.endpoint_custom import dao as endpoint_custom_dao
from xivo_dao.resources.endpoint_sccp import dao as endpoint_sccp_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.func_key_template import dao as template_dao
from xivo_dao.resources.switchboard import dao as switchboard_dao

from wazo_provd_client import Client as ProvdClient

from wazo_confd.plugins.line.service import build_service as build_line_service
from wazo_confd.plugins.user_line.service import (
    build_service as build_user_line_service,
)
from .resource import UserItem, UserList
from .resource_sub import (
    UserForwardBusy,
    UserForwardList,
    UserForwardNoAnswer,
    UserForwardUnconditional,
    UserServiceDND,
    UserServiceIncallFilter,
    UserServiceList,
)
from wazo_confd.plugins.line_extension.service import (
    build_service as build_extension_line_service,
)
from wazo_confd.plugins.endpoint_sip.service import (
    build_endpoint_service as build_endpoint_sip_service,
)
from wazo_confd.plugins.line_endpoint.service import build_service_custom
from wazo_confd.plugins.line_endpoint.service import build_service_sip
from wazo_confd.plugins.line_endpoint.service import build_service_sccp
from wazo_confd.plugins.endpoint_sccp.service import (
    build_service as build_endpoint_sccp_service,
)
from wazo_confd.plugins.endpoint_custom.service import (
    build_service as build_endpoint_custom_service,
)
from wazo_confd.plugins.extension.service import (
    build_service as build_extension_service,
)
from wazo_confd.plugins.incall_extension.service import (
    build_service as build_incall_extension_service,
)
from wazo_confd.plugins.incall.service import build_service as build_incall_service
from wazo_confd.plugins.user_group.service import (
    build_service as build_user_group_service,
)
from wazo_confd.plugins.func_key.service import build_user_funckey_template_service
from wazo_confd.plugins.switchboard_member.service import (
    build_service as build_user_switchboard_service,
)

from .service import build_service, build_service_callservice, build_service_forward
from ..user_import.wazo_user_service import build_service as build_wazo_user_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        pjsip_doc = dependencies['pjsip_doc']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        user_service = build_service(provd_client)
        wazo_user_service = build_wazo_user_service()
        service_callservice = build_service_callservice()
        service_forward = build_service_forward()
        line_service = build_line_service(provd_client)
        extension_service = build_extension_service(provd_client)
        user_line_service = build_user_line_service()
        endpoint_custom_service = build_endpoint_custom_service()
        endpoint_sip_service = build_endpoint_sip_service(provd_client, pjsip_doc)
        endpoint_sccp_service = build_endpoint_sccp_service()
        extension_line_service = build_extension_line_service()
        line_endpoint_custom_association_service = build_service_custom(provd_client)
        line_endpoint_sip_association_service = build_service_sip(provd_client)
        line_endpoint_sccp_association_service = build_service_sccp(provd_client)
        incall_service = build_incall_service()
        incall_extension_service = build_incall_extension_service()
        user_group_service = build_user_group_service()
        user_funckey_template_association_service = build_user_funckey_template_service(
            provd_client
        )
        user_switchboard_service = build_user_switchboard_service()

        api.add_resource(
            UserItem,
            '/users/<uuid:id>',
            '/users/<int:id>',
            endpoint='users',
            resource_class_args=(user_service,),
        )

        api.add_resource(
            UserList,
            '/users',
            endpoint='users_list',
            resource_class_args=(
                user_service,
                line_service,
                user_line_service,
                endpoint_custom_service,
                endpoint_sip_service,
                extension_line_service,
                extension_service,
                line_endpoint_custom_association_service,
                line_endpoint_sip_association_service,
                line_endpoint_sccp_association_service,
                endpoint_sccp_service,
                wazo_user_service,
                incall_service,
                incall_extension_service,
                user_group_service,
                user_funckey_template_association_service,
                user_switchboard_service,
                endpoint_custom_dao,
                endpoint_sccp_dao,
                line_dao,
                user_dao,
                sip_dao,
                transport_dao,
                incall_dao,
                extension_dao,
                group_dao,
                template_dao,
                switchboard_dao,
            ),
        )

        api.add_resource(
            UserServiceDND,
            '/users/<uuid:user_id>/services/dnd',
            '/users/<int:user_id>/services/dnd',
            resource_class_args=(service_callservice,),
        )

        api.add_resource(
            UserServiceIncallFilter,
            '/users/<uuid:user_id>/services/incallfilter',
            '/users/<int:user_id>/services/incallfilter',
            resource_class_args=(service_callservice,),
        )

        api.add_resource(
            UserServiceList,
            '/users/<uuid:user_id>/services',
            '/users/<int:user_id>/services',
            resource_class_args=(service_callservice,),
        )

        api.add_resource(
            UserForwardBusy,
            '/users/<uuid:user_id>/forwards/busy',
            '/users/<int:user_id>/forwards/busy',
            resource_class_args=(service_forward,),
        )

        api.add_resource(
            UserForwardNoAnswer,
            '/users/<uuid:user_id>/forwards/noanswer',
            '/users/<int:user_id>/forwards/noanswer',
            resource_class_args=(service_forward,),
        )

        api.add_resource(
            UserForwardUnconditional,
            '/users/<uuid:user_id>/forwards/unconditional',
            '/users/<int:user_id>/forwards/unconditional',
            resource_class_args=(service_forward,),
        )

        api.add_resource(
            UserForwardList,
            '/users/<uuid:user_id>/forwards',
            '/users/<int:user_id>/forwards',
            resource_class_args=(service_forward,),
        )
