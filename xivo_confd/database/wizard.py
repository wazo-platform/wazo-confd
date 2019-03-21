# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.alchemy.general import General
from xivo_dao.alchemy.netiface import Netiface
from xivo_dao.alchemy.resolvconf import Resolvconf
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.helpers.db_manager import Session


def set_language(language):

    row = Session.query(StaticSIP).filter(StaticSIP.var_name == 'language').first()
    row.var_val = language
    Session.add(row)

    row = Session.query(StaticIAX).filter(StaticIAX.var_name == 'language').first()
    row.var_val = language
    Session.add(row)

    row = Session.query(SCCPGeneralSettings).filter(SCCPGeneralSettings.option_name == 'language').first()
    row.option_value = language
    Session.add(row)


def set_timezone(timezone):
    row = Session.query(General).first()
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
    Session.add(Netiface(ifname=interface,
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
                         description='Wizard Configuration'))


def set_context_switchboard(tenant_uuid):
    Session.add(Context(name='__switchboard_directory',
                        displayname='Switchboard',
                        contexttype='others',
                        description='',
                        tenant_uuid=str(tenant_uuid)))


def set_context_internal(context, tenant_uuid):
    Session.add(Context(name='default',
                        displayname=context['display_name'],
                        contexttype='internal',
                        description='',
                        tenant_uuid=str(tenant_uuid)))

    Session.add(ContextNumbers(context='default',
                               type='user',
                               numberbeg=context['number_start'],
                               numberend=context['number_end']))


def set_context_incall(context, tenant_uuid):
    Session.add(Context(name='from-extern',
                        displayname=context['display_name'],
                        contexttype='incall',
                        description='',
                        tenant_uuid=str(tenant_uuid)))

    if context.get('number_start') and context.get('number_end'):
        Session.add(ContextNumbers(context='from-extern',
                                   type='incall',
                                   numberbeg=context['number_start'],
                                   numberend=context['number_end'],
                                   didlength=context['did_length']))


def set_context_outcall(context, tenant_uuid):
    Session.add(Context(name='to-extern',
                        displayname=context['display_name'],
                        contexttype='outcall',
                        description='',
                        tenant_uuid=str(tenant_uuid)))


def include_outcall_context_in_internal_context():
    Session.add(ContextInclude(context='default',
                               include='to-extern',
                               priority=0))


def set_xivo_configured():
    row = Session.query(General).first()
    row.configured = True
    Session.add(row)


def get_xivo_configured():
    return Session.query(General).first()


def create(wizard, tenant_uuid):
    network = wizard['network']

    set_language(wizard['language'])
    set_netiface(network['interface'], network['ip_address'], network['netmask'], network['gateway'])
    set_resolvconf(network['hostname'], network['domain'], network['nameservers'])
    set_timezone(wizard['timezone'])
    set_context_switchboard(tenant_uuid)
    set_context_incall(wizard['context_incall'], tenant_uuid)
    set_context_internal(wizard['context_internal'], tenant_uuid)
    set_context_outcall(wizard['context_outcall'], tenant_uuid)
    include_outcall_context_in_internal_context()
