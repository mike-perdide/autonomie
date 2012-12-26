# -*- coding: utf-8 -*-
# * File Name :
#
# * Copyright (C) 2010 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 03-09-2012
# * Last Modified :
#
# * Project :
#
"""
    The estimation model
"""
import datetime
import logging

from zope.interface import implementer

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import deferred
from sqlalchemy.orm import backref
# Aye : ici on a du double dans la bdd, en attendant une éventuelle
# migration des données, on dépend entièrement de mysql
from sqlalchemy.dialects.mysql import DOUBLE

from autonomie.models.types import CustomDateType
from autonomie.models.types import CustomDateType2
from autonomie.models.utils import get_current_timestamp
from autonomie.models import DBBASE
from autonomie.models import default_table_args

from .compute import TaskCompute
from .interfaces import IValidatedTask
from .interfaces import IMoneyTask
from .invoice import Invoice
from .invoice import InvoiceLine
from .task import Task
from .task import DiscountLine
from .states import DEFAULT_STATE_MACHINES

log = logging.getLogger(__name__)


@implementer(IValidatedTask, IMoneyTask)
class Estimation(Task, TaskCompute):
    """
        Estimation Model
    """
    __tablename__ = 'estimation'
    __table_args__ = default_table_args
    id = Column("id", ForeignKey('task.id'), primary_key=True, nullable=False)
    sequenceNumber = Column("sequenceNumber", Integer, nullable=False)
    _number = Column("number", String(100), nullable=False)
    tva = Column("tva", Integer, nullable=False, default=196)
    deposit = Column("deposit", Integer, default=0)
    paymentConditions = deferred(
        Column("paymentConditions", Text),
        group='edit')
    exclusions = deferred(Column("exclusions", Text), group='edit')
    project_id = Column("project_id", ForeignKey('project.id'))
    client_id = Column('client_id', Integer, ForeignKey('customer.id'))
    manualDeliverables = deferred(
        Column("manualDeliverables", Integer),
        group='edit')
    course = deferred(
        Column('course', Integer, nullable=False, default=0),
        group='edit')
    displayedUnits = deferred(
        Column('displayedUnits', Integer, nullable=False, default=0),
        group='edit')
    discountHT = Column('discountHT', Integer, default=0)
    expenses = deferred(
        Column('expenses', Integer, default=0),
        group='edit')
    paymentDisplay = deferred(
        Column('paymentDisplay', String(20), default="SUMMARY"),
        group='edit')
    address = Column("address", Text, default="")
    project = relationship(
        "Project",
        backref=backref('estimations', order_by='Estimation.taskDate')
    )
    client = relationship(
            "Client",
            primaryjoin="Client.id==Estimation.client_id",
            backref=backref('estimations', order_by='Estimation.taskDate'))

    __mapper_args__ = {'polymorphic_identity': 'estimation', }

    state_machine = DEFAULT_STATE_MACHINES['estimation']

    def is_draft(self):
        return self.CAEStatus in ('draft', 'invalid',)

    def is_editable(self, manage=False):
        if manage:
            return self.CAEStatus in ('draft', 'invalid', 'wait', None)
        else:
            return self.CAEStatus in ('draft', 'invalid', None)

    def is_valid(self):
        return self.CAEStatus == 'valid'

    def has_been_validated(self):
        return self.CAEStatus in ('valid', 'geninv',)

    def is_waiting(self):
        return self.CAEStatus == 'wait'

    def is_estimation(self):
        return True

    def duplicate(self, user, project, phase, client):
        """
            returns a duplicate estimation object
        """
        seq_number = project.get_next_estimation_number()
        date = datetime.date.today()

        estimation = Estimation()
        estimation.statusPersonAccount = user
        estimation.phase = phase
        estimation.owner = user
        estimation.client = client
        estimation.project = project
        estimation.taskDate = date
        estimation.set_sequenceNumber(seq_number)
        estimation.set_number()
        estimation.set_name()
        if client.id == self.client_id:
            estimation.address = self.address
        else:
            estimation.address = client.full_adress

        estimation.description = self.description
        estimation.CAEStatus = "draft"

        estimation.deposit = self.deposit
        estimation.paymentConditions = self.paymentConditions
        estimation.exclusions = self.exclusions
        estimation.manualDeliverables = self.manualDeliverables
        estimation.course = self.course
        estimation.displayedUnits = self.displayedUnits
        estimation.discountHT = self.discountHT
        estimation.expenses = self.expenses
        estimation.paymentDisplay = self.paymentDisplay
        for line in self.lines:
            estimation.lines.append(line.duplicate())
        for line in self.payment_lines:
            estimation.payment_lines.append(line.duplicate())
        for line in self.discounts:
            estimation.discounts.append(line.duplicate())
        return estimation

    def _account_invoiceline(self, amount, description, tva=1960):
        """
            Return an account invoiceline
        """
        return InvoiceLine(cost=amount, description=description, tva=tva)

    def _make_deposit(self, invoice, tva):
        """
            Return a deposit invoice
        """
        invoice.taskDate = datetime.date.today()
        invoice.displayedUnits = 0
        invoice.set_name(deposit=True)
        invoice.set_number(deposit=True)

        amount = self.deposit_amount()
        description = u"Facture d'acompte"
        line = self._account_invoiceline(amount, description, tva)
        invoice.lines.append(line)
        return invoice, line.duplicate()

    def _make_intermediary(self, invoice, paymentline, tva):
        """
            return an intermediary invoice described by "paymentline"
        """
        invoice.taskDate = paymentline.paymentDate
        invoice.displayedUnits = 0
        invoice.set_name()
        invoice.set_number()
        if self.manualDeliverables:
            amount = paymentline.amount
        else:
            amount = self.paymentline_amount()
        description = paymentline.description
        line = self._account_invoiceline(amount, description, tva)
        invoice.lines.append(line)
        return invoice, line.duplicate()

    def _sold_invoice_lines(self, account_lines):
        """
            return the lines that will appear in the sold invoice
        """
        sold_lines = []
        for line in self.lines:
            sold_lines.append(line.gen_invoice_line())
        rowIndex = len(self.lines)
        for line in account_lines:
            rowIndex = rowIndex + 1
            line.cost = -1 * line.cost
            line.rowIndex = rowIndex
            sold_lines.append(line)
        return sold_lines

    def _make_sold(self, invoice, paymentline, paid_lines, is_sold):
        """
            Return the sold invoice
        """
        invoice.taskDate = paymentline.paymentDate
        invoice.set_name(sold=is_sold)
        invoice.set_number()

        invoice.displayedUnits = self.displayedUnits
        invoice.expenses = self.expenses
        for line in self._sold_invoice_lines(paid_lines):
            invoice.lines.append(line)
        for line in self.discounts:
            invoice.discounts.append(line.duplicate())
        return invoice

    def _get_common_invoice(self, seq_number, user):
        """
            Return an invoice object with common args for
            all the generated invoices
        """
        inv = Invoice()
        # Relationship
        inv.client = self.client
        inv.project = self.project
        inv.phase = self.phase
        inv.owner = user
        inv.statusPersonAccount = user
        inv.estimation = self

        # Common args
        inv.paymentConditions=self.paymentConditions
        inv.description=self.description
        inv.course=self.course
        inv.address = self.address
        inv.CAEStatus = "draft"
        inv.set_sequenceNumber(seq_number)
        return inv

    def gen_invoices(self, user):
        """
            Return the invoices based on the current estimation
        """
        invoices = []
        # Used to mark the existence of intermediary invoices
        is_sold = len(self.payment_lines) > 1
        # Used to store the amount of the intermediary invoices
        lines = []
        # Sequence number that will be incremented by hand
        seq_number = self.project.get_next_invoice_number()
        # Fix temporaire pour le montant de la tva pour les acomptes et autres
        # On prend la première tva qu'on trouve
        tvas = self.get_tvas().keys()
        tva = tvas[0]
        if self.deposit > 0:
            invoice = self._get_common_invoice(seq_number, user)
            deposit, line = self._make_deposit(invoice, tva)
            invoices.append(deposit)
            # We remember the lines to display them in the last invoice
            lines.append(line)
            seq_number += 1
        # all payment lines specified (less the last one)
        for pline in self.payment_lines[:-1]:
            invoice = self._get_common_invoice(seq_number, user)
            invoice, line = self._make_intermediary(invoice, pline, tva)
            invoices.append(invoice)
            lines.append(line)
            seq_number += 1

        invoice = self._get_common_invoice(seq_number, user)
        pline = self.payment_lines[-1]
        invoice = self._make_sold(invoice, pline, lines, is_sold)
        invoices.append(invoice)
        return invoices

    def set_name(self):
        taskname_tmpl = u"Devis {0}"
        self.name = taskname_tmpl.format(self.sequenceNumber)

    def set_number(self):
        tasknumber_tmpl = u"D{s.sequenceNumber}_{s.taskDate:%m%y}"
        self._number = tasknumber_tmpl.format(s=self)

    def set_sequenceNumber(self, snumber):
        self.sequenceNumber = snumber

    @property
    def number(self):
        tasknumber_tmpl = u"{s.project.code}_{s.client.code}_{s._number}"
        return tasknumber_tmpl.format(s=self)

    def is_cancelled(self):
        """
            Return True if the invoice has been cancelled
        """
        return self.CAEStatus == 'aboest'

    # Computing
    def deposit_amount(self):
        """
            Compute the amount of the deposit
        """
        if self.deposit > 0:
            total = self.total_ht()
            return int(total * int(self.deposit) / 100.0)
        return 0

    def get_nb_payment_lines(self):
        """
            Returns the number of payment lines configured
        """
        return len(self.payment_lines)

    def paymentline_amount(self):
        """
            Compute payment lines amounts in case of equal payment repartition
            (when manualDeliverables is 0)
            (when the user has checked 3 times)
        """
        total = self.total_ht()
        deposit = self.deposit_amount()
        rest = total - deposit
        return int(rest / self.get_nb_payment_lines())

    # Computations for estimation display
    def deposit_amount_ttc(self):
        """
            Return the ttc amount of the deposit (for estimation display)
        """
        if self.deposit > 0:
            total_ttc = self.total_ttc()
            return int(total_ttc * int(self.deposit) / 100.0)
        return 0

    def sold(self):
        """
            Compute the sold amount to finish on an exact value
            if we divide 10 in 3, we'd like to have something like :
                3.33 3.33 3.34
            (for estimation display)
        """
        result = 0
        total_ttc = self.total()
        deposit_ttc = self.deposit_amount_ttc()
        rest = total_ttc - deposit_ttc

        payment_lines_num = self.get_nb_payment_lines()
        if payment_lines_num == 1 or not self.get_nb_payment_lines():
            # No other payment line
            result = rest
        else:
            if self.manualDeliverables == 0:
                # Amounts has to be divided
                line_amount = self.paymentline_amount()
                result = rest - ((payment_lines_num - 1) * line_amount)
            else:
                # Ici la donnée est fausse (on va rajouter de la tva sur les
                # montants des lignes de paiement configurées manuellement
                # Donc le solde caluclé ici est faux
                result = rest - sum(line.amount
                                    for line in self.payment_lines[:-1])
        return result

    def add_line(self, line=None, **kwargs):
        """
            Add a line to the current task
        """
        if line is None:
            line = EstimationLine(**kwargs)
        self.lines.append(line)

    def add_discount(self, line=None, **kwargs):
        """
            Add a discount line to the current task
        """
        if line is None:
            line = DiscountLine(**kwargs)
        self.discounts.append(line)

    def add_payment(self, line=None, **kwargs):
        """
            Add a payment line to the current task
        """
        if line is None:
            line = PaymentLine(**kwargs)
        self.payments.append(line)

    def set_lines(self, lines):
        """
            Set the lines
        """
        self.lines = lines

    def set_discounts(self, lines):
        """
            Set the discounts
        """
        self.discounts = lines

    def set_payments(self, lines):
        """
            set the payment lines
        """
        self.payments = lines

    def __repr__(self):
        return u"<Estimation id:{s.id}>".format(s=self)


class EstimationLine(DBBASE):
    """
        Estimation lines
    """
    __tablename__ = 'estimation_line'
    __table_args__ = default_table_args
    id = Column("id", Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('estimation.id', ondelete="cascade"))
    rowIndex = Column("rowIndex", Integer)
    description = Column("description", Text)
    cost = Column(Integer, default=0)
    quantity = Column(DOUBLE, default=1)
    tva = Column("tva", Integer, nullable=False, default=196)
    creationDate = deferred(
        Column("creationDate",
            CustomDateType,
            default=get_current_timestamp))
    updateDate = deferred(
        Column("updateDate",
            CustomDateType,
            default=get_current_timestamp,
            onupdate=get_current_timestamp))
    unity = Column("unity", String(10))
    task = relationship(
        "Estimation",
        backref=backref("lines", order_by='EstimationLine.rowIndex',
                        cascade="all, delete-orphan"))

    def duplicate(self):
        """
            duplicate a line
        """
        newone = EstimationLine()
        newone.rowIndex = self.rowIndex
        newone.cost = self.cost
        newone.description = self.description
        newone.quantity = self.quantity
        newone.tva = self.tva
        newone.unity = self.unity
        return newone

    def gen_invoice_line(self):
        """
            return the equivalent InvoiceLine
        """
        line = InvoiceLine()
        line.rowIndex = self.rowIndex
        line.cost = self.cost
        line.description = self.description
        line.quantity = self.quantity
        line.tva = self.tva
        line.unity = self.unity
        return line

    def total_ht(self):
        """
            Compute the line's total
        """
        return float(self.cost) * float(self.quantity)

    def tva_amount(self, totalht=None):
        """
            compute the tva amount of a line
        """
        totalht = self.total_ht()
        result = float(totalht) * (max(int(self.tva), 0) / 10000.0)
        return result

    def total(self):
        return self.tva_amount() + self.total_ht()

    def __repr__(self):
        return u"<EstimationLine id:{s.id} task_id:{s.task_id} cost:{s.cost}\
 quantity:{s.quantity} tva:{s.tva}".format(s=self)


class PaymentLine(DBBASE):
    """
        payments lines
    """
    __tablename__ = 'estimation_payment'
    __table_args__ = default_table_args
    id = Column("id", Integer, primary_key=True, nullable=False)
    task_id = Column(Integer, ForeignKey('estimation.id', ondelete="cascade"))
    rowIndex = Column("rowIndex", Integer)
    description = Column("description", Text)
    amount = Column("amount", Integer)
    creationDate = deferred(
        Column("creationDate",
            CustomDateType,
            default=get_current_timestamp))
    updateDate = deferred(
        Column("updateDate",
            CustomDateType,
            default=get_current_timestamp,
            onupdate=get_current_timestamp))
    paymentDate = Column("paymentDate", CustomDateType2(11))
    task = relationship(
        "Estimation",
        backref=backref('payment_lines', order_by='PaymentLine.rowIndex',
            cascade="all, delete-orphan"))

    def duplicate(self):
        """
            duplicate a paymentline
        """
        return PaymentLine(rowIndex=self.rowIndex,
                             amount=self.amount,
                             description=self.description,
                             paymentDate=datetime.date.today())

    def __repr__(self):
        return u"<PaymentLine id:{s.id} task_id:{s.task_id} amount:{s.amount}\
 date:{s.paymentDate}".format(s=self)
