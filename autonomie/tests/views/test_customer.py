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

from autonomie.models.customer import Customer
from autonomie.views.customer import CustomerAdd, CustomerEdit, customer_view
from autonomie.tests.base import BaseFunctionnalTest

APPSTRUCT = {'name':'Company', 'contactLastName':u'Lastname',
             'contactFirstName':u'FirstName',
             'address':'Address should be multiline',
             'compte_cg':"Compte CG1515",
             'compte_tiers':"Compte Tiers"}


class Base(BaseFunctionnalTest):
    def addOne(self):
        self.config.add_route('customer', '/')
        view = CustomerAdd(self.get_csrf_request())
        view.submit_success(APPSTRUCT)

    def getOne(self):
        try:
            return Customer.query().filter(Customer.name=='Company').one()
        except:
            return None

class TestCustomerAdd(Base):
    def test_success(self):
        self.addOne()
        customer = self.getOne()
        for attr, value in APPSTRUCT.items():
            self.assertEqual(getattr(customer, attr), value)


class TestCustomerEdit(Base):
    def test_customer_edit(self):
        self.addOne()
        customer = self.getOne()
        req = self.get_csrf_request()
        req.context = customer
        appstruct = APPSTRUCT.copy()
        appstruct['contactLastName'] = u"Changed Lastname"
        appstruct['compte_cg'] = "1"
        appstruct['compte_tiers'] = "2"
        view = CustomerEdit(req)
        view.submit_success(appstruct)
        customer = self.getOne()
        self.assertEqual(customer.contactLastName, u'Changed Lastname')
        self.assertEqual(customer.compte_cg, "1")
        self.assertEqual(customer.compte_tiers, "2")
