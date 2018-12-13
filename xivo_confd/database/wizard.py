# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.alchemy.cti_contexts import CtiContexts
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctidirectoryfields import CtiDirectoryFields
from xivo_dao.alchemy.ctireversedirectories import CtiReverseDirectories
from xivo_dao.alchemy.directories import Directories
from xivo_dao.alchemy.entity import Entity
from xivo_dao.alchemy.general import General
from xivo_dao.alchemy.netiface import Netiface
from xivo_dao.alchemy.resolvconf import Resolvconf
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.helpers.db_manager import Session


def set_default_entity(display_name, name, tenant_uuid):
    row = Entity(displayname=display_name, name=name, description='Wizard Entity', tenant_uuid=tenant_uuid)
    Session.add(row)


def entity_unique_name(display_name):
    return ''.join(c for c in display_name if c.isalnum()).lower()


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


def set_context_switchboard(entity, tenant_uuid):
    Session.add(Context(name='__switchboard_directory',
                        displayname='Switchboard',
                        entity=entity,
                        contexttype='others',
                        description='',
                        tenant_uuid=str(tenant_uuid)))


def set_context_internal(context, entity, tenant_uuid):
    Session.add(Context(name='default',
                        displayname=context['display_name'],
                        entity=entity,
                        contexttype='internal',
                        description='',
                        tenant_uuid=str(tenant_uuid)))

    Session.add(ContextNumbers(context='default',
                               type='user',
                               numberbeg=context['number_start'],
                               numberend=context['number_end']))


def set_context_incall(context, entity, tenant_uuid):
    Session.add(Context(name='from-extern',
                        displayname=context['display_name'],
                        entity=entity,
                        contexttype='incall',
                        description='',
                        tenant_uuid=str(tenant_uuid)))

    if context.get('number_start') and context.get('number_end'):
        Session.add(ContextNumbers(context='from-extern',
                                   type='incall',
                                   numberbeg=context['number_start'],
                                   numberend=context['number_end'],
                                   didlength=context['did_length']))


def set_context_outcall(context, entity, tenant_uuid):
    Session.add(Context(name='to-extern',
                        displayname=context['display_name'],
                        entity=entity,
                        contexttype='outcall',
                        description='',
                        tenant_uuid=str(tenant_uuid)))


def set_phonebook(entity, phonebook_body):
    directories = Directories(uri='postgresql://asterisk:proformatique@localhost/asterisk',
                              dirtype='dird_phonebook',
                              name='phonebook',
                              description='Wazo phonebook',
                              dird_tenant=entity,
                              dird_phonebook=phonebook_body['name'])
    Session.add(directories)
    Session.commit()
    cti_directories = CtiDirectories(name='wazophonebook',
                                     match_direct='["firstname", "lastname", "displayname", "society", "number_office"]',
                                     match_reverse='["number_office", "number_mobile"]',
                                     description='Default Wazo phonebook',
                                     deletable=1,
                                     directory_id=directories.id)
    Session.add(cti_directories)
    Session.commit()
    name = '{firstname} {lastname}'
    fields = [
        ('fullname', name),
        ('name', name),
        ('display_name', '{displayname}'),
        ('phone', '{number_office}'),
        ('phone_mobile', '{number_mobile}'),
        ('phone_home', '{number_home}'),
        ('phone_other', '{number_other}'),
        ('company', '{society}'),
        ('reverse', name),
    ]
    for name, value in fields:
        Session.add(CtiDirectoryFields(dir_id=cti_directories.id,
                                       fieldname=name,
                                       value=value))

    for profile in Session.query(CtiContexts).all():
        raw_directories = profile.directories
        if not raw_directories:
            available_directories = []
        else:
            available_directories = profile.directories.split(',')
        available_directories.append('wazophonebook')
        profile.directories = ','.join(available_directories)
        Session.add(profile)
    Session.add(CtiReverseDirectories(directories='["wazophonebook"]'))


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
    entity = entity_unique_name(wizard['entity_name'])

    set_default_entity(wizard['entity_name'], entity, tenant_uuid)
    set_language(wizard['language'])
    set_netiface(network['interface'], network['ip_address'], network['netmask'], network['gateway'])
    set_resolvconf(network['hostname'], network['domain'], network['nameservers'])
    set_timezone(wizard['timezone'])
    set_context_switchboard(entity, tenant_uuid)
    set_context_incall(wizard['context_incall'], entity, tenant_uuid)
    set_context_internal(wizard['context_internal'], entity, tenant_uuid)
    set_context_outcall(wizard['context_outcall'], entity, tenant_uuid)
    include_outcall_context_in_internal_context()
