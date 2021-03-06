# -*- coding: utf-8 -*-
# * Copyright (C) 2012-2013 Croissance Commune
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * Pettier Gabriel;
#       * TJEBBES Gaston <g.t@majerti.fr>
#
# This file is part of Autonomie : Progiciel de gestion de CAE.
#
#    Autonomie is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Autonomie is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Autonomie.  If not, see <http://www.gnu.org/licenses/>.
#

"""
    Tests
"""
from mock import MagicMock
from pyramid import testing

from autonomie.tests.base import BaseFunctionnalTest
from autonomie.tests.base import BaseViewTest

class TestAuth(BaseFunctionnalTest):
    """
        Test the auth form and redirect
    """
    def test_redirect(self):
        login_url = "http://localhost/login?nextpage=%2F"
        res = self.app.get('/')
        self.assertEqual(res.status_int, 302)
        self.assertIn(login_url, dict(res.headerlist).values())

def get_avatar():
    user = MagicMock(name=u'test', companies=[])
    user.is_admin = lambda :False
    user.is_manager = lambda :False
    user.companies = [MagicMock(name=u'Test', id=100), MagicMock(name=u'Test2', id=101)]
    return user

def get_avatar2():
    user = MagicMock(name=u'test2')
    user.is_admin = lambda :False
    user.is_manager = lambda :False
    user.companies = [MagicMock(name=u'Test', id=100)]
    return user

class TestIndex(BaseViewTest):
    def test_index_view(self):
        from autonomie.views.index import index
        self.config.add_route('company', '/company/{id}')
        self.config.add_static_view('static', 'autonomie:static')
        request = self.get_csrf_request()
        avatar = get_avatar()
        request._user = avatar
        request.user = avatar
        response = index(request)
        self.assertEqual(avatar.companies, response['companies'])
        avatar = get_avatar2()
        request._user = avatar
        request.user = avatar
        response = index(request)
        self.assertEqual(response.status_int, 302)
