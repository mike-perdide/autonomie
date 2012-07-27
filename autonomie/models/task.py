# -*- coding: utf-8 -*-
# * File Name : task.py
#
# * Copyright (C) 2010 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 25-07-2012
# * Last Modified :
#
# * Project :
#
"""
    Model for base tasks

    Sqldump for a task :
      `IDTask` int(11) NOT NULL auto_increment, #identifiant de la tâche
      `IDPhase` int(11) NOT NULL,           # identifiant de la phase associée
      `name` varchar(150) NOT NULL,         # Nom de la tâche

      `CAEStatus` varchar(10) default NULL, # Statut de la tâche
             valid/abort/paid/draft/geninv/aboinv/aboest/sent/wait/none/recinv
      `statusComment` text,                 # Commentaire sur le statut
                                 communication entrepr/CAE
                                 information de paiement ([par chèque ...])
      `statusPerson` int(11) default NULL,  #Id de la personne associée
                                                aux informations de status
      `statusDate` int(11) default NULL,

      `customerStatus` varchar(10) default NULL, # Reste vide
      `taskDate` int(11) default '0',       # Date
      `IDEmployee` int(11) NOT NULL,        #Id de la personne propriétaire
      `document` varchar(255) default NULL,
      `creationDate` int(11) NOT NULL,
      `updateDate` int(11) NOT NULL,
      `description` text,                   #description
      `documentType` varchar(255) default NULL, # header à envoyer pour
                                l'ouverture du document
                                (doit être réservé aux tâches personnalisées)
      `rank` int(11) default NULL,  # Ordre des tâches
      PRIMARY KEY  (`IDTask`),
      KEY `IDPhase` (`IDPhase`),
      KEY `IDEmployee` (`IDEmployee`)
"""
import datetime
import logging

from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implements
from zope.interface import implementer

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Date
from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.orm import deferred
from sqlalchemy.orm import backref
from sqlalchemy import func

from autonomie.models.types import CustomDateType
from autonomie.models.types import CustomDateType2
from autonomie.models.utils import get_current_timestamp
from autonomie.models import DBBASE
from autonomie.utils.exception import Forbidden

log = logging.getLogger(__name__)

class ITask(Interface):
    """
        Task interface, need to be implemented by all documents
    """
    def get_status_str():
        """
            Provide a human readble string for the current task status
        """

    def is_invoice():
        """
            is the current task an invoice ?
        """

    def is_estimation():
        """
            Is the current task an estimation ?
        """

    def is_cancelinvoice():
        """
            Is the current task a cancelled invoice ?
        """

class IValidatedTask(ITask):
    """
        Interface for task needing to be validated by the office
    """
    def is_draft():
        """
            Return the draft status of a document
        """

    def is_editable(manage):
        """
            Is the current task editable ?
        """

    def is_valid():
        """
            Is the current task valid
        """

    def has_been_validated():
        """
            Has the current task been validated ?
        """

    def is_waiting():
        """
            Is the current task waiting for approval
        """

    def is_sent():
        """
            Has the current document been sent to a client
        """

    def is_cancelled():
        """
            Has the current document been cancelled
        """

class IPaidTask(IValidatedTask):
    """
        Task interface for task needing to be paid
    """
    def is_tolate():
        """
            Is the payment of the current task to late ?
        """

    def is_paid():
        """
            Has the current task been paid
        """


class IInvoice(Interface):
    """
        Invoice interface (used to get an uniform invoice list display
        See templates/invoices.mako (under invoice.model) to see the expected
        common informations
    """
    statusComment = Attribute("""statusComment to allow discussion""")
    statusDate = Attribute("""The date the status has last been changed""")
    officialNumber = Attribute("""official number used in sage""")
    taskDate = Attribute("""Date of the task""")
    id = Attribute("""the document sql id""")
    IDTask = Attribute("""Another name for the id""")
    number = Attribute("""the document's non official number""")
    description = Attribute("""the document description string""")

    def get_company():
        """
            Return the company this task is related to
        """

    def get_client():
        """
            Return the client this document is related to
        """

    def is_paid():
        """
            Has the current task been paid
        """

    def is_cancelled():
        """
            Has the current document been cancelled
        """

    def is_tolate():
        """
            Is it too late
        """

    def is_invoice():
        """
            is the current task an invoice ?
        """

    def is_cancelinvoice():
        """
            Is the current task a cancelled invoice ?
        """

    def get_paymentmode_str():
        """
            Return the string for the payment mode display
        """

DEF_STATUS = u"Statut inconnu"
STATUS = dict((
            ("draft", u"Brouillon modifié",),
            ("wait", u"Validation demandée",),
            ("valid", u"Validé{genre}"),
            ('invalid', u"Invalidé{genre}",),
            ("abort", u"Annulé{genre}",),
            ("geninv", u"Facture générée",),
            ("aboinv", u"Facture annulée",),
            ("aboest", u"Devis annulé",),
            ("sent", u"Document envoyé",),
            ("paid", u"Paiement reçu",),
            ("recinv", u"Client relancé",),
            ))

@implementer(ITask)
class Task(DBBASE):
    """
        Metadata pour une tâche (estimation, invoice)
    """
    __tablename__ = 'coop_task'
    __table_args__ = {'mysql_engine': 'MyISAM', "mysql_charset":'utf8'}
    __mapper_args__ = {'polymorphic_identity':'task'}

    IDTask = Column(Integer, primary_key=True)
    IDPhase = Column("IDPhase", ForeignKey('coop_phase.IDPhase'))
    name = Column("name", String(255))
    CAEStatus = Column('CAEStatus', String(10))
    statusComment = Column("statusComment", Text)
    statusPerson = Column("statusPerson",
                          ForeignKey('egw_accounts.account_id'))
    statusDate = Column("statusDate", CustomDateType,
                                        default=get_current_timestamp,
                                        onupdate=get_current_timestamp)
    taskDate = Column("taskDate", CustomDateType2)
    IDEmployee = Column("IDEmployee",
                            ForeignKey('egw_accounts.account_id'))
    creationDate = deferred(Column("creationDate", CustomDateType,
                                            default=get_current_timestamp))
    updateDate = Column("updateDate", CustomDateType,
                                        default=get_current_timestamp,
                                        onupdate=get_current_timestamp)
    description = Column("description", Text)
    statusPersonAccount = relationship("User",
                        primaryjoin="Task.statusPerson==User.id",
                        backref="taskStatuses")
    owner = relationship("User",
                        primaryjoin="Task.IDEmployee==User.id",
                            backref="ownedTasks")


    def get_status_suffix(self):
        """
            return the status suffix for rendering a pretty status string
        """
        if self.statusPersonAccount:
            firstname = self.statusPersonAccount.firstname
            lastname = self.statusPersonAccount.lastname
        else:
            firstname = "Inconnu"
            lastname = ""
        if self.statusDate:
            if isinstance(self.statusDate, datetime.date) or \
                    isinstance(self.statusDate, datetime.datetime):
                date = self.statusDate.strftime("%d/%m/%Y")
            else:
                date = ""
        else:
            date = ""
        return u" par {firstname} {lastname} le {date}".format(
                firstname=firstname, lastname=lastname, date=date)

    def get_status_str(self):
        """
            Return human readable string for task status
            Task are actually simple documents
        """
        status_str = u"Déposé"
        return status_str + self.get_status_suffix()

    def is_invoice(self):
        return False

    def is_estimation(self):
        return False

    def is_cancelinvoice(self):
        return False

    @validates('CAEStatus')
    def validate_status(self, key, status):
        """
            validate the caestatus change
        """
        message = u"Vous n'êtes pas autorisé à assigner ce statut {0} à ce \
document."
        log.debug(u"# CAEStatus change #")
        actual_status = self.CAEStatus
        log.debug(u" + was {0}, becomes {1}".format(actual_status, status))
        message = message.format(status)
        if status in ('draft', 'wait',):
            if not actual_status in (None, 'draft', 'invalid'):
                raise Forbidden(message)
        elif status in ('valid',):
            if self.is_cancelinvoice():
                if not actual_status in ('draft',):
                    raise Forbidden(message)
            elif not actual_status in ('wait',):
                raise Forbidden(message)
        elif status in ('invalid',):
            if not actual_status in ('wait', ):
                raise Forbidden(message)
        elif status in ('aboest',):
            if not actual_status in ('valid', 'sent', 'invalid', 'wait'):
                raise Forbidden(message)
        elif status in ('geninv',):
            if not actual_status in ('valid', 'sent', ):
                raise Forbidden(message)
        elif status in ('sent',):
            if not actual_status in ('valid', "recinv"):
                raise Forbidden(message)
        elif status in ('paid',):
            if not actual_status in ('valid', 'sent', "recinv"):
                raise Forbidden(message)
        elif status in ('aboinv', 'abort',):
            if not actual_status in ('valid', 'sent', "recinv", "invalid", \
                                                                    "wait"):
                raise Forbidden(message)
        elif status in ('recinv',):
            if not actual_status in ('valid', 'sent', "recinv",):
                raise Forbidden(message)
        else:
            assert False
        return status

    def get_company(self):
        """
            Return the company owning this task
        """
        if self.project:
            return self.project.company
        else:
            return None

    def get_client(self):
        """
            Return the client of the current task
        """
        if self.project:
            return self.project.client
        else:
            return None

    def get_company_id(self):
        """
            Return the id of the company owning this task
        """
        return self.project.company.id

    @property
    def id(self):
        return self.IDTask

@implementer(IValidatedTask)
class Estimation(Task):
    """
        Estimation Model
    """
    __tablename__ = 'coop_estimation'
    __table_args__ = {'mysql_engine': 'MyISAM', "mysql_charset":'utf8'}
    IDTask = Column("IDTask", ForeignKey('coop_task.IDTask'),
                primary_key=True, nullable=False)
    sequenceNumber = Column("sequenceNumber", Integer,
                nullable=False)
    number = Column("number", String(100), nullable=False)
    tva = Column("tva", Integer, nullable=False, default=196)
    deposit = Column("deposit", Integer, default=0)
    paymentConditions = deferred(Column("paymentConditions", Text),
                        group='edit')
    exclusions = deferred(Column("exclusions", Text),
                        group='edit')
    IDProject = Column("IDProject", ForeignKey('coop_project.IDProject'))
    manualDeliverables = deferred(Column("manualDeliverables", Integer),
                        group='edit')
    course = deferred(Column('course', Integer,
                                    nullable=False, default=0),
                                    group='edit')
    displayedUnits = deferred(Column('displayedUnits', Integer,
                                    nullable=False, default=0),
                                    group='edit')
    discountHT = Column('discountHT', Integer, default=0)
    expenses = deferred(Column('expenses', Integer, default=0),
                                group='edit')
    paymentDisplay = deferred(Column('paymentDisplay', String(20),
                                                default="SUMMARY"),
                                                group='edit')
    project = relationship("Project",
                            backref=backref('estimations',
                                            order_by='Estimation.taskDate')
                            )
    phase =  relationship("Phase",
                          backref=backref("estimations",
                          order_by='Estimation.taskDate'))
    __mapper_args__ = {
                        'polymorphic_identity':'estimation',
                       }

    #ITask interface
    def get_status_str(self):
        status_str = STATUS.get(self.CAEStatus, DEF_STATUS).format(genre=u"")
        return status_str + self.get_status_suffix()

    def is_draft(self):
        return self.CAEStatus in ('draft', 'invalid',)

    def is_editable(self, manage=False):
        if manage:
            return self.CAEStatus in ('draft', 'invalid', 'wait',)
        else:
            return self.CAEStatus in ('draft', 'invalid')

    def is_valid(self):
        return self.CAEStatus == 'valid'

    def has_been_validated(self):
        return self.CAEStatus in ('valid', 'geninv', 'sent',)

    def is_waiting(self):
        return self.CAEStatus == 'wait'

    def is_sent(self):
        return self.CAEStatus == "sent"


    def is_estimation(self):
        return True

    def get_next_actions(self):
        """
            Return the next available actions regarding the current status
        """
        matchdict = dict(draft=['wait', 'duplicate'],
                         wait=['valid', 'invalid', 'duplicate'],
                         invalid=['wait', 'duplicate'],
                         valid=['sent', 'aboest', 'geninv', 'duplicate'],
                         sent=['aboest', 'geninv', 'duplicate', ],
                         aboest=['delete'],
                         geninv=['duplicate'])
        return matchdict[self.CAEStatus]

    def duplicate(self):
        """
            returns a duplicate estimation object
        """
        duple = Estimation()
        duple.IDPhase = self.IDPhase
        duple.taskDate = datetime.date.today()
        duple.IDEmployee = self.IDEmployee
        duple.description = self.description

        duple.tva = self.tva
        duple.deposit = self.deposit
        duple.paymentConditions = self.paymentConditions
        duple.exclusions = self.exclusions
        duple.IDProject = self.IDProject
        duple.manualDeliverables = self.manualDeliverables
        duple.course = self.course
        duple.displayedUnits = self.displayedUnits
        duple.discountHT = self.discountHT
        duple.expenses = self.expenses
        duple.paymentDisplay = self.paymentDisplay
        return duple

    def is_deletable(self):
        """
            Returns True if the estimation could be deleted
        """
        return self.CAEStatus not in ('geninv',)

    def is_cancelled(self):
        """
            Return True if the invoice has been cancelled
        """
        return self.CAEStatus == 'aboest'

@implementer(IPaidTask, IInvoice)
class Invoice(Task):
    """
        Invoice Model
    """
    __tablename__ = 'coop_invoice'
    __table_args__ = {'mysql_engine': 'MyISAM', "mysql_charset":'utf8'}
    __mapper_args__ = {
                       'polymorphic_identity':'invoice',
                       }
    IDTask = Column("IDTask", ForeignKey('coop_task.IDTask'), primary_key=True)
    IDEstimation = Column("IDEstimation", ForeignKey('coop_estimation.IDTask'))
    IDProject = Column("IDProject", ForeignKey('coop_project.IDProject'))
    sequenceNumber = Column("sequenceNumber", Integer, nullable=False)
    number = Column("number", String(100), nullable=False)
    tva = Column("tva", Integer, nullable=False, default=196)
    paymentConditions = deferred(Column("paymentConditions", Text),
                                 group='edit')
    deposit = deferred(Column('deposit', Integer, nullable=False, default=0),
                       group='edit')
    course = deferred(Column('course', Integer, nullable=False, default=0),
                      group='edit')
    officialNumber = Column("officialNumber", Integer)
    paymentMode = Column("paymentMode", String(10))
    displayedUnits = deferred(Column('displayedUnits', Integer,
                                    nullable=False, default=0),
                                    group='edit')
    discountHT = Column('discountHT', Integer, default=0)
    expenses = deferred(Column('expenses', Integer, default=0), group='edit')

    project = relationship("Project", backref=backref('invoices',
                                            order_by='Invoice.taskDate'))
    phase =  relationship("Phase", backref=backref("invoices",
                                                order_by='Invoice.taskDate'))
    estimation = relationship("Estimation",
                      backref="invoice",
                      primaryjoin="Invoice.IDEstimation==Estimation.IDTask")

    def get_status_str(self):
        status_str = STATUS.get(self.CAEStatus, DEF_STATUS).format(genre=u'e')
        return status_str + self.get_status_suffix()

    def is_draft(self):
        return self.CAEStatus in ('draft', 'invalid',)

    def is_editable(self, manage=False):
        if manage:
            return self.CAEStatus in ('draft', 'invalid', 'wait',)
        else:
            return self.CAEStatus in ('draft', 'invalid',)

    def is_valid(self):
        return self.CAEStatus == 'valid'

    def has_been_validated(self):
        return self.CAEStatus in ('valid', 'geninv', 'sent', "recinv",)

    def is_waiting(self):
        return self.CAEStatus == "wait"

    def is_sent(self):
        return self.CAEStatus == "sent"

    def is_invoice(self):
        return True

    def is_paid(self):
        return self.CAEStatus == 'paid'

    def is_cancelled(self):
        """
            Return True is the invoice has been cancelled
        """
        return self.CAEStatus == 'aboinv'

    def is_tolate(self):
        """
            Return True if a payment is expected since more than
            45 days
        """
        today = datetime.date.today()
        elapsed = today - self.taskDate
        if elapsed > datetime.timedelta(days=45):
            tolate = True
        else:
            tolate = False
        return self.CAEStatus in ('valid', 'sent','recinv') and tolate

    def get_next_actions(self):
        """
            Return the next available actions regarding the current status
        """
        matchdict = dict(draft=['wait', 'duplicate'],
                       wait=['valid', 'invalid', 'duplicate'],
                       invalid=['wait', 'duplicate'],
                       valid=['sent', 'aboinv', 'paid', 'duplicate', 'recinv'],
                       sent=['aboinv', 'paid', 'duplicate', 'recinv' ],
                       aboinv=['delete'],
                       paid=['duplicate'])
        return matchdict[self.CAEStatus]

    def get_paymentmode_str(self):
        """
            Return a user-friendly string describing the payment Mode
        """
        if self.paymentMode == 'CHEQUE':
            return u"par chèque"
        elif self.paymentMode == 'VIREMENT':
            return u"par virement"
        else:
            return u"mode paiement inconnu"

    @validates("paymentMode")
    def validate_paymentMode(self, key, paymentMode):
        """
            Validate the paymentMode
        """
        if not paymentMode in ('CHEQUE', 'VIREMENT'):
            raise Forbidden(u'Mode de paiement inconnu')
        return paymentMode

    @classmethod
    def get_officialNumber(cls, dbsession):
        """
            Return the next officialNumber available in the Invoice's table
            Take the max of official Number
            when taskDate startswith the current year
            taskdate is a string (YYYYMMDD)
        """
        current_year = datetime.date.today().year
        return dbsession.query(func.max(Invoice.officialNumber)).filter(
                Invoice.taskDate.between(current_year*10000,
                                         (current_year+1)*10000
                                    ))

    def gen_cancel_invoice(self):
        """
            Return a cancel invoice with self's informations
        """
        cancelinvoice = CancelInvoice()
        cancelinvoice.IDPhase = self.IDPhase
        cancelinvoice.CAEStatus = 'draft'
        cancelinvoice.taskDate = datetime.date.today()
        cancelinvoice.description = self.description

        cancelinvoice.IDInvoice = self.IDTask
        cancelinvoice.IDProject = self.IDProject
        cancelinvoice.invoiceDate = self.taskDate
        cancelinvoice.invoiceNumber = self.officialNumber
        cancelinvoice.expenses = -1 * self.expenses
        cancelinvoice.displayedUnits = self.displayedUnits
        cancelinvoice.tva = self.tva
        return cancelinvoice

@implementer(IPaidTask, IInvoice)
class CancelInvoice(Task):
    """
        CancelInvoice model
        Could also be called negative invoice
    """
    __tablename__ = 'coop_cancel_invoice'
    __table_args__ = {'mysql_engine': 'MyISAM', "mysql_charset":'utf8'}
    __mapper_args__ = {'polymorphic_identity':'cancelinvoice'}
    IDTask = Column(Integer, ForeignKey('coop_task.IDTask'), primary_key=True)

    IDInvoice = Column(Integer, ForeignKey('coop_invoice.IDTask'),
                                                        default=None)
    IDProject = Column(Integer, ForeignKey('coop_project.IDProject'))
    sequenceNumber = deferred(Column(Integer), group='edit')
    number = Column(String(100))
    tva = Column(Integer, default=1960)
    reimbursementConditions = deferred(Column(String(255), default=None),
            group='edit')
    officialNumber = deferred(Column(Integer, default=None), group='edit')
    paymentMode = deferred(Column(String(80), default=None), group='edit')
    displayedUnits = Column(Integer, default=0)
    expenses = deferred(Column(Integer, default=0), group='edit')

    project = relationship("Project", backref=backref('cancelinvoices',
                                            order_by='CancelInvoice.taskDate')
                            )
    phase = relationship("Phase",
                          backref=backref("cancelinvoices",
                                          order_by='CancelInvoice.taskDate')
                          )
    invoice = relationship("Invoice",
                      backref="cancelinvoice",
                      primaryjoin="CancelInvoice.IDInvoice==Invoice.IDTask")

    def get_status_str(self):
        status_str = STATUS.get(self.CAEStatus, DEF_STATUS).format(genre=u'')
        if self.CAEStatus == 'paid':
            status_str = u"Réglé"
        return status_str + self.get_status_suffix()


    def is_draft(self):
        return self.CAEStatus in ('draft', 'invalid')

    def is_editable(self, manage=False):
        return self.CAEStatus == 'draft'

    def is_valid(self):
        return self.CAEStatus == 'valid'

    def has_been_validated(self):
        return self.CAEStatus in ('valid', 'sent', "recinv",)

    def is_waiting(self):
        return self.CAEStatus == 'wait'

    def is_sent(self):
        return self.CAEStatus == "sent"

    def is_cancelinvoice(self):
        return True

    def is_paid(self):
        return self.CAEStatus == 'paid'

    def is_cancelled(self):
        return False

    def get_paymentmode_str(self):
        """
            Return a user-friendly string describing the payment Mode
        """
        if self.paymentMode == 'CHEQUE':
            return u"par chèque"
        elif self.paymentMode == 'VIREMENT':
            return u"par virement"
        else:
            return u"mode paiement inconnu"

    @classmethod
    def get_officialNumber(cls, dbsession):
        """
            Return the greatest officialNumber actually used in the
            ManualInvoice table
        """
        current_year = datetime.date.today().year
        return dbsession.query(func.max(CancelInvoice.officialNumber)).filter(
                    func.year(CancelInvoice.taskDate) == current_year)

    def is_tolate(self):
        """
            Return False
        """
        return False

@implementer(IInvoice)
class ManualInvoice(DBBASE):
    """
        Modèle pour les factures manuelles (ancienne version)
    """
    __tablename__ = 'symf_facture_manuelle'
    __table_args__ = {'mysql_engine': 'MyISAM', "mysql_charset":'utf8'}
    id_ = Column('id', BigInteger, primary_key=True)
    officialNumber = Column('sequence_id', BigInteger)
    description = Column('libelle', String(255))
    montant_ht = Column("montant_ht", Integer)
    tva = Column("tva", Integer)
    payment_ok = Column("paiement_ok", Integer)
    statusDate = Column("paiement_date", Date())
    paymentMode = Column("paiement_comment", String(255))
    client_id = Column('client_id', String(5),
                            ForeignKey('coop_customer.code'))
    taskDate = Column("date_emission", Date(),
                                default=datetime.datetime.now)
    company_id = Column('compagnie_id', BigInteger,
                            ForeignKey('coop_company.IDCompany'))
    created_at = deferred(Column("created_at", DateTime,
                                      default=datetime.datetime.now))
    updated_at = deferred(Column("updated_at", DateTime,
                                      default=datetime.datetime.now,
                                      onupdate=datetime.datetime.now))
    client = relationship("Client",
                primaryjoin="Client.id==ManualInvoice.client_id",
                  backref='manual_invoices')
    company = relationship("Company",
                primaryjoin="Company.id==ManualInvoice.company_id",
                  backref='manual_invoices')
    @property
    def statusComment(self):
        return None

    @property
    def statusDate(self):
        return None

    @property
    def id(self):
        return None

    @property
    def IDTask(self):
        return None

    @property
    def number(self):
        """
            return the invoice number
        """
        return u"FACT_MAN_{0}".format(self.officialNumber)

    def get_company(self):
        return self.company

    def get_client(self):
        return self.client

    def is_paid(self):
        return self.payment_ok == 1

    def is_cancelled(self):
        return False

    def is_tolate(self):
        today = datetime.date.today()
        elapsed = today - self.taskDate
        return not self.is_paid() and elapsed > datetime.timedelta(days=45)

    def get_paymentmode_str(self):
        """
            Return the payment mode string
        """
        if self.paymentMode == u'chèque':
            return u"par chèque"
        elif self.paymentMode == u'virement':
            return u"par virement"
        else:
            return u""

    @validates("paymentMode")
    def validate_paymentMode(self, key, paymentMode):
        """
            Validate the paymentMode
        """
        if not paymentMode in (u'chèque', u'virement'):
            raise Forbidden(u'Mode de paiement inconnu')
        return paymentMode


    def is_cancelinvoice(self):
        """
            return false
        """
        return False

    def is_invoice(self):
        """
            return false
        """
        return False

    @classmethod
    def get_officialNumber(cls, dbsession):
        """
            Return the greatest officialNumber actually used in the
            ManualInvoice table
        """
        current_year = datetime.date.today().year
        return dbsession.query(func.max(ManualInvoice.officialNumber)).filter(
                    func.year(ManualInvoice.taskDate) == current_year)