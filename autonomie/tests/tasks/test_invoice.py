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

import datetime
from mock import MagicMock
from autonomie.tests.base import BaseTestCase, printstatus
from autonomie.models.task import (CancelInvoice, ManualInvoice,
                                    Invoice, InvoiceLine, DiscountLine)
from autonomie.models.user import User
from autonomie.models.customer import Customer
from autonomie.models.project import Phase, Project

LINES = [{'description':u'text1',
          'cost':10025,
           'tva':1960,
          'unity':'DAY',
          'quantity':1.25,
          'rowIndex':1},
         {'description':u'text2',
          'cost':7500,
           'tva':1960,
          'unity':'month',
          'quantity':3,
          'rowIndex':2}]

DISCOUNTS = [{'description':u"Remise à 19.6", 'amount':2000, 'tva':1960}]

INVOICE = dict( name=u"Facture 2",
                sequenceNumber=2,
                taskDate=datetime.date(2012, 12, 10), #u"10-12-2012",
                description=u"Description de la facture",
                _number=u"invoicenumber",
                expenses=0,
                expenses_ht=0)

class TestCancelInvoice(BaseTestCase):
    def test_set_name(self):
        cinv = CancelInvoice()
        cinv.set_sequenceNumber(5)
        cinv.set_name()
        self.assertEqual(cinv.name, u"Avoir 5")

    def test_get_number(self):
        cinv = CancelInvoice()
        cinv.project = MagicMock(code="PRO1")
        cinv.customer = MagicMock(code="CLI1")
        cinv.taskDate = datetime.date(1969, 07, 31)
        cinv.set_sequenceNumber(15)
        cinv.set_number()
        self.assertEqual(cinv.number, u"PRO1_CLI1_A15_0769")

class TestManualInvoice(BaseTestCase):
    def test_tva_amount(self):
        m = ManualInvoice(montant_ht=1950)
        self.assertEqual(m.tva_amount(), 0)

class TestInvoice(BaseTestCase):

    def getOne(self):
        inv = Invoice(**INVOICE)
        for line in LINES:
            inv.lines.append(InvoiceLine(**line))
        for discount in DISCOUNTS:
            inv.discounts.append(DiscountLine(**discount))
        return inv

    def test_set_name(self):
        invoice = Invoice()
        invoice.set_sequenceNumber(5)
        invoice.set_name()
        self.assertEqual(invoice.name, u"Facture 5")
        invoice.set_name(sold=True)
        self.assertEqual(invoice.name, u"Facture de solde")
        invoice.set_name(deposit=True)
        self.assertEqual(invoice.name, u"Facture d'acompte 5")

    def test_set_number(self):
        invoice = Invoice()
        invoice.customer = MagicMock(code="CLI1")
        invoice.project = MagicMock(code="PRO1")
        seq_number = 15
        invoice.set_sequenceNumber(15)
        invoice.set_name()
        date = datetime.date(1969, 07, 31)
        invoice.taskDate = date
        invoice.set_number()
        self.assertEqual(invoice.number, u"PRO1_CLI1_F15_0769")
        invoice.set_number(deposit=True)
        self.assertEqual(invoice.number, u"PRO1_CLI1_FA15_0769")

    def test_gen_cancelinvoice(self):
        user = User.query().first()
        project = Project.query().first()
        inv = self.getOne()
        inv.project = project
        inv.owner = user
        inv.statusPersonAccount = user

        self.session.add(inv)
        self.session.flush()
        cinv = inv.gen_cancelinvoice(user)
        self.session.add(cinv)
        self.session.flush()

        self.assertEqual(cinv.name, "Avoir 1")
        self.assertEqual(cinv.total_ht(), -1 * inv.total_ht())
        today = datetime.date.today()
        self.assertEqual(cinv.taskDate, today)

    def test_gen_cancelinvoice_payment(self):
        user = User.query().first()
        project = Project.query().first()
        inv = self.getOne()
        inv.project = project
        inv.owner = user
        inv.statusPersonAccount = user
        inv.record_payment(mode="c", amount=1500)
        cinv = inv.gen_cancelinvoice(user)
        self.assertEqual(len(cinv.lines),
                          len(inv.lines) + len(inv.discounts) + 1)
        self.assertEqual(cinv.lines[-1].cost, 1500)

    def test_duplicate_invoice(self):
        user = self.session.query(User).first()
        customer = self.session.query(Customer).first()
        project = self.session.query(Project).first()
        phase = self.session.query(Phase).first()
        inv = self.getOne()
        inv.owner = user
        inv.statusPersonAccount = user
        inv.project = project
        inv.phase = phase
        inv.customer = customer

        newinv = inv.duplicate(user, project, phase, customer)
        self.assertEqual(len(inv.lines), len(newinv.lines))
        self.assertEqual(len(inv.discounts), len(newinv.discounts))
        self.assertEqual(inv.project, newinv.project)
        self.assertEqual(newinv.statusPersonAccount, user)
        self.assertEqual(newinv.phase, phase)
        for key in "customer", "address", "expenses", "expenses_ht":
            self.assertEqual(getattr(newinv, key), getattr(inv, key))

    def test_duplicate_invoice_financial_year(self):
        user = self.session.query(User).first()
        customer = self.session.query(Customer).first()
        project = self.session.query(Project).first()
        phase = self.session.query(Phase).first()
        inv = self.getOne()
        inv.owner = user
        inv.statusPersonAccount = user
        inv.project = project
        inv.phase = phase
        inv.customer = customer
        inv.financial_year = 1900

        newinv = inv.duplicate(user, project, phase, customer)
        self.assertEqual(newinv.financial_year, datetime.date.today().year)

    def test_duplicate_invoice_integration(self):
        user = self.session.query(User).first()
        printstatus(user)
        project = self.session.query(Project).first()
        phase = self.session.query(Phase).first()
        customer = self.session.query(Customer).first()

        inv = self.getOne()
        inv.phase = phase
        inv.customer = customer
        inv.owner = user
        inv.statusPersonAccount = user
        inv.project = project
        self.session.add(inv)
        self.session.flush()
        newest = inv.duplicate(user, project, phase, customer)
        self.session.add(newest)
        self.session.flush()
        self.assertEqual(newest.phase_id, phase.id)
        self.assertEqual(newest.owner_id, user.id)
        self.assertEqual(newest.statusPerson, user.id)
        self.assertEqual(newest.project_id, project.id)

#
#    def test_valid_invoice(self):
#        inv = get_invoice(stripped=True)
#        self.session.add(inv)
#        self.session.flush()
#        self.config.testing_securitypolicy(userid='test', permissive=True)
#        request = testing.DummyRequest()
#        inv.set_status('wait', request, 1)
#        self.session.merge(inv)
#        self.session.flush()
#        inv.set_status('valid', request, 1)
#        today = datetime.date.today()
#        self.assertEqual(inv.taskDate, today)
#        self.assertEqual(inv.officialNumber, 1)
#
#    def test_valid_payment(self):
#        inv = get_invoice(stripped=True)
#        self.session.add(inv)
#        self.session.flush()
#        self.config.testing_securitypolicy(userid='test', permissive=True)
#        request = testing.DummyRequest()
#        inv.set_status('wait', request, 1)
#        self.session.merge(inv)
#        self.session.flush()
#        inv.set_status('valid', request, 1)
#        self.session.merge(inv)
#        self.session.flush()
#        inv.set_status("paid", request, 1, amount=150, mode="CHEQUE")
#        inv = self.session.merge(inv)
#        self.session.flush()
#        invoice = self.session.query(Invoice)\
#                .filter(Invoice.id==inv.id).first()
#        self.assertEqual(invoice.CAEStatus, 'paid')
#        self.assertEqual(len(invoice.payments), 1)
#        self.assertEqual(invoice.payments[0].amount, 150)
