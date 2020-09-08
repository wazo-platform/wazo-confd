# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import and_

from xivo_dao.alchemy.asterisk_file import AsteriskFile
from xivo_dao.alchemy.asterisk_file_section import AsteriskFileSection
from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable
from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.infos import Infos
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.netiface import Netiface
from xivo_dao.alchemy.resolvconf import Resolvconf
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_manager import Session


def find_transport_udp():
    rows = Session.query(PJSIPTransport)
    for row in rows.all():
        for key, value in row.options:
            if key == 'protocol' and value == 'udp':
                return row


def insert_context(body):
    context = Context(**body)
    Session.add(context)


def insert_endpoint_sip(body):
    endpoint_sip = EndpointSIP(**body)
    Session.add(endpoint_sip)
    Session.flush()
    return str(endpoint_sip.uuid)


def insert_line(body):
    line = LineFeatures(provisioningid=0, context=body['context'])
    line.endpoint_sip_uuid = body['endpoint_sip_uuid']
    Session.add(line)


def insert_tenant(tenant_uuid):
    tenant = Tenant(uuid=tenant_uuid)
    Session.add(tenant)
    Session.flush()


def set_default_outbound_endpoint(endpoint_name):
    file_ = (
        Session.query(AsteriskFile).filter(AsteriskFile.name == 'pjsip.conf').first()
    )
    section = (
        Session.query(AsteriskFileSection)
        .filter(
            and_(
                AsteriskFileSection.asterisk_file_id == file_.id,
                AsteriskFileSection.name == 'global',
            )
        )
        .first()
    )
    Session.add(
        AsteriskFileVariable(
            key='default_outbound_endpoint',
            value=endpoint_name,
            asterisk_file_section_id=section.id,
        )
    )


def set_language(language):

    row = Session.query(StaticSIP).filter(StaticSIP.var_name == 'language').first()
    row.var_val = language
    Session.add(row)

    row = Session.query(StaticIAX).filter(StaticIAX.var_name == 'language').first()
    row.var_val = language
    Session.add(row)

    row = (
        Session.query(SCCPGeneralSettings)
        .filter(SCCPGeneralSettings.option_name == 'language')
        .first()
    )
    row.option_value = language
    Session.add(row)


def set_timezone(timezone):
    row = Session.query(Infos).first()
    row.timezone = timezone
    Session.add(row)


def set_resolvconf(hostname, domain, nameservers):
    row = Session.query(Resolvconf).first()
    row.hostname = hostname
    row.domain = domain
    row.search = domain
    row.description = 'Wizard Configuration'
    row.nameserver1 = nameservers[0]
    if len(nameservers) > 1:
        row.nameserver2 = nameservers[1]
        if len(nameservers) > 2:
            row.nameserver3 = nameservers[2]

    Session.add(row)


def set_netiface(interface, address, netmask, gateway):
    Session.add(
        Netiface(
            ifname=interface,
            hwtypeid=1,
            networktype='voip',
            type='iface',
            family='inet',
            method='static',
            address=address,
            netmask=netmask,
            broadcast='',
            gateway=gateway,
            mtu=1500,
            options='',
            description='Wizard Configuration',
        )
    )


def set_wazo_configured():
    row = Session.query(Infos).first()
    row.configured = True
    Session.add(row)


def get_wazo_configured():
    return Session.query(Infos).first()


def create(wizard):
    network = wizard['network']

    set_language(wizard['language'])
    set_netiface(
        network['interface'],
        network['ip_address'],
        network['netmask'],
        network['gateway'],
    )
    set_resolvconf(network['hostname'], network['domain'], network['nameservers'])
    set_timezone(wizard['timezone'])
