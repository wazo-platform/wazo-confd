# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextnumbers import ContextNumbers
from xivo_dao.alchemy.entity import Entity
from xivo_dao.alchemy.general import General
from xivo_dao.alchemy.netiface import Netiface
from xivo_dao.alchemy.resolvconf import Resolvconf
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.user import User
from xivo_dao.helpers.db_manager import Session


def set_admin_password(password):
    row = Session.query(User).filter(User.login == 'root').first()
    row.passwd = password
    Session.add(row)


def set_autoprov_name(autoprov_username):
    Session.add(StaticSIP(category='general',
                          filename='sip.conf',
                          var_name='autocreate_prefix',
                          var_val=autoprov_username))


def set_default_entity(display_name, name):
    row = Entity(displayname=display_name, name=name, description='Wizard Entity')
    Session.add(row)


def get_entity(display_name):
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


def set_context_switchboard(entity):
    Session.add(Context(name='__switchboard_directory',
                        displayname='Switchboard',
                        entity=entity,
                        contexttype='others',
                        description=''))


def set_context_internal(context, entity):
    Session.add(Context(name='default',
                        displayname=context['display_name'],
                        entity=entity,
                        contexttype='internal',
                        description=''))

    Session.add(ContextNumbers(context='default',
                               type='user',
                               numberbeg=context['number_start'],
                               numberend=context['number_end']))


def set_context_incall(context, entity):
    Session.add(Context(name='from-extern',
                        displayname=context['display_name'],
                        entity=entity,
                        contexttype='incall',
                        description=''))

    if context.get('number_start') and context.get('number_end'):
        Session.add(ContextNumbers(context='from-extern',
                                   type='incall',
                                   numberbeg=context['number_start'],
                                   numberend=context['number_end'],
                                   didlength=context['did_length']))


def set_context_outcall(context, entity):
    Session.add(Context(name='to-extern',
                        displayname=context['display_name'],
                        entity=entity,
                        contexttype='outcall',
                        description=''))


def set_xivo_configured():
    row = Session.query(General).first()
    row.configured = True
    Session.add(row)


def get_xivo_configured():
    return Session.query(General).first()


def created(wizard, autoprov_username):
    network = wizard['network']
    entity = get_entity(wizard['entity_name'])

    set_admin_password(wizard['admin_password'])
    set_autoprov_name(autoprov_username)
    set_default_entity(wizard['entity_name'], entity)
    set_language(wizard['language'])
    set_netiface(network['interface'], network['ip_address'], network['netmask'], network['gateway'])
    set_resolvconf(network['hostname'], network['domain'], network['nameservers'])
    set_timezone(wizard['timezone'])
    set_context_switchboard(entity)
    set_context_incall(wizard['context_incall'], entity)
    set_context_internal(wizard['context_internal'], entity)
    set_context_outcall(wizard['context_outcall'], entity)
