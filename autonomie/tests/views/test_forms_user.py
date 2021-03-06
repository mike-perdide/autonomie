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

from colander import Invalid
from mock import MagicMock
from autonomie.views.forms.user import (is_useredit_form, unique_login, auth,
        PasswordChangeSchema, deferred_company_disable_default)
from autonomie.models.user import User

from colander import SchemaNode

from autonomie.tests.base import BaseTestCase

def adduser(dbsession):
    user = User(login='test_forms_user',
                lastname='lastname__éé',
                firstname='firstname__éé')
    user.set_password(u"Tést$!Pass")
    dbsession.add(user)
    dbsession.flush()
    return user

class TestFormsUser(BaseTestCase):
    def test_isuseredit_form(self):
        req = MagicMock(context=MagicMock(__name__='user'))
        self.assertTrue(is_useredit_form(req))
        req = MagicMock(context=MagicMock(__name__='other'))
        self.assertFalse(is_useredit_form(req))

    def test_unique_login(self):
        adduser(self.session)
        self.assertRaises(Invalid, unique_login, "nutt", "test_forms_user")
        unique_login("nutt", "other unused login")

    def test_auth(self):
        adduser(self.session)
        form = PasswordChangeSchema()
        appstruct = {'login':'test_forms_user', 'password':u"Tést$!Pass"}
        auth(form, appstruct)
        appstruct = {'login':'test_forms_user', 'password':u"Tést$"}
        self.assertRaises(Invalid, auth, form, appstruct)

    def test_default_disable(self):
        companies = [MagicMock(employees=range(2))]
        user = MagicMock(companies=companies)
        req = MagicMock(context=user)
        self.assertFalse(deferred_company_disable_default("", {'request': req}))
        companies = [MagicMock(employees=[1])]
        user = MagicMock(companies=companies)
        req = MagicMock(context=user)
        self.assertTrue(deferred_company_disable_default("", {'request': req}))
