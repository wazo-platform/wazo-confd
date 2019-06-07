# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.asterisk import AsteriskConfigurationList


class RTPGeneralList(AsteriskConfigurationList):
    section_name = 'general'

    @required_acl('confd.asterisk.rtp.general.get')
    def get(self):
        return super(RTPGeneralList, self).get()

    @required_acl('confd.asterisk.rtp.general.update')
    def put(self):
        return super(RTPGeneralList, self).put()


class RTPIceHostCandidatesList(AsteriskConfigurationList):
    section_name = 'ice_host_candidates'

    @required_acl('confd.asterisk.rtp.ice_host_candidates.get')
    def get(self):
        return super(RTPIceHostCandidatesList, self).get()

    @required_acl('confd.asterisk.rtp.ice_host_candidates.update')
    def put(self):
        return super(RTPIceHostCandidatesList, self).put()
