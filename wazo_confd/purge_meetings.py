# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging

from datetime import datetime, timedelta, timezone

from wazo import xivo_logging
from wazo.chain_map import ChainMap
from wazo.config_helper import read_config_file_hierarchy
from xivo_dao import init_db_from_config
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.infos import dao as info_dao
from xivo_dao.resources.meeting import dao as meeting_dao
from xivo_dao.resources.meeting_authorization import dao as meeting_authorization_dao

from wazo_auth_client import Client as AuthClient

from wazo_confd._bus import BusPublisher
from wazo_confd._sysconfd import SysconfdPublisher
from wazo_confd.config import DEFAULT_CONFIG, _load_key_file
from wazo_confd.helpers.resource import CRUDService
from wazo_confd.plugins.meeting.validator import (
    build_validator as build_meeting_validator,
)
from wazo_confd.plugins.ingress_http.service import (
    build_service as build_ingress_http_service,
)
from wazo_confd.plugins.extension_feature.service import (
    build_service as build_extension_features_service,
)
from wazo_confd.plugins.meeting.notifier import Notifier as MeetingNotifier
from wazo_confd.plugins.meeting_authorization.notifier import (
    Notifier as MeetingAuthorizationNotifier,
)
from wazo_confd.plugins.meeting_authorization.service import (
    build_service as build_authorization_service,
)

logger = logging.getLogger('wazo-confd-purge-meetings')


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Log debug messages",
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Only print warnings and errors',
    )
    parser.add_argument(
        '--authorizations-only',
        action='store_true',
        help='Only remove old meeting authorizations, not meeting themselves.',
    )
    parsed_args = parser.parse_args()
    result = {'log_level': logging.INFO}
    if parsed_args.quiet:
        result['log_level'] = logging.WARNING
    elif parsed_args.debug:
        result['log_level'] = logging.DEBUG
    result['authorizations_only'] = parsed_args.authorizations_only
    return result


def load_config():
    file_config = read_config_file_hierarchy(ChainMap(DEFAULT_CONFIG))
    service_key = _load_key_file(ChainMap(file_config, DEFAULT_CONFIG))
    return ChainMap(service_key, file_config, DEFAULT_CONFIG)


def remove_meetings_older_than(date, meeting_service):
    logger.info('Removing meetings older than %s...', date)

    with session_scope() as session:
        meetings = meeting_dao.find_all_by(created_before=date, persistent=False)
        logger.info('Found %s meeting.', len(meetings))
        for meeting in meetings:
            logger.debug('Removing meeting %s: %s', meeting.uuid, meeting.name)
            meeting_service.delete(meeting)
        session.flush()


def remove_meeting_authorizations_older_than(date, meeting_authorization_service):
    logger.info('Removing meeting authorizations older than %s...', date)

    with session_scope() as session:
        meeting_authorizations = meeting_authorization_dao.find_all_by(
            meeting_uuid=None,
            created_before=date,
        )
        logger.info('Found %s meeting authorizations.', len(meeting_authorizations))
        for meeting_authorization in meeting_authorizations:
            logger.debug(
                'Removing authorization for meeting %s: uuid "%s", guest_name "%s"',
                meeting_authorization.meeting_uuid,
                meeting_authorization.uuid,
                meeting_authorization.guest_name,
            )
            meeting_authorization_service.delete(meeting_authorization)
        session.flush()


def get_master_tenant_uuid(auth_config):
    client = AuthClient(**auth_config)
    token_data = client.token.new(expiration=1)
    return token_data['metadata']['tenant_uuid']


def main():
    cli_args = parse_cli_args()
    config = load_config()
    xivo_logging.setup_logging('/dev/null', log_level=cli_args['log_level'])
    xivo_logging.silence_loggers(['stevedore.extension'], logging.WARNING)

    tenant_uuid = get_master_tenant_uuid(config['auth'])
    init_db_from_config(config)

    wazo_uuid = info_dao.get().uuid
    if 'uuid' not in config:
        config['uuid'] = wazo_uuid

    bus = BusPublisher.from_config(config['uuid'], config['bus'])
    sysconfd = SysconfdPublisher.from_config(config)

    if not cli_args['authorizations_only']:
        ingress_http_service = build_ingress_http_service()
        extension_features_service = build_extension_features_service()
        meeting_service = CRUDService(
            meeting_dao,
            build_meeting_validator(),
            MeetingNotifier(
                bus,
                sysconfd,
                ingress_http_service,
                extension_features_service,
                tenant_uuid,
            ),
        )

        meeting_date_limit = datetime.now(timezone.utc) - timedelta(hours=24)
        remove_meetings_older_than(meeting_date_limit, meeting_service)

    authorization_notifier = MeetingAuthorizationNotifier(bus)
    meeting_authorization_service = build_authorization_service(authorization_notifier)

    meeting_authorization_date_limit = datetime.now(timezone.utc) - timedelta(hours=24)
    remove_meeting_authorizations_older_than(
        meeting_authorization_date_limit, meeting_authorization_service
    )

    sysconfd.flush()
    bus.flush()
