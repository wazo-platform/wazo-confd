# -*- coding: UTF-8 -*-
# Copyright (C) 2012  Avencall
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
from flask import session
from functools import wraps
import authdigest
import flask
import logging

logger = logging.getLogger(__name__)


class FlaskRealmDigestDB(authdigest.RealmDigestDB):
    def requires_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            request = flask.request
            #if request.remote_addr != '127.0.0.1':
            if 'logged' not in session and not self.isAuthenticated(request):
                logger.debug("Challenging")
                return self.challenge()
                #return make_response('', 401)
            else:
                if 'logged' in session and session['logged']:
                    logger.debug("Session déjà enregistrée!!!!!!")
                else:
                    session['logged'] = True
                    logger.debug("Nouvelle session créée!!!!!")
                return f(*args, **kwargs)
            #return f(*args, **kwargs)
        return decorated

authDB = FlaskRealmDigestDB('XivoRestRealm')
#authDB.add_user('admin', 'test')
