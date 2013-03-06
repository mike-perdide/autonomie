# -*- coding: utf-8 -*-
# * File Name : treasury.py
#
# * Copyright (C) 2012 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 04-02-2013
# * Last Modified :
#
# * Project : Autonomie
#
"""
    Models related to the treasury module
"""
from datetime import date
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Enum
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

from autonomie.models.base import DBBASE
from autonomie.models.base import default_table_args

class TurnoverProjection(DBBASE):
    """
        Turnover projection
        :param company_id: The company this projection is related to
        :param month: The month number this projection is made for
        :param year: The year this projection is made for
    """
    __tablename__ = 'turnover_projection'
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="cascade"))
    month = Column(Integer)
    year = Column(Integer)
    comment = Column(Text, default="")
    value = Column(Integer)
    company = relationship("Company",
            backref=backref("turnoverprojections",
                order_by="TurnoverProjection.month",
                cascade="all, delete-orphan"))


class ExpenseType(DBBASE):
    """
        Base Type for expenses
        :param label: Label of the expense type that will be used in the UI
        :param code: Analytic code related to this expense
        :param type: Column for polymorphic discrimination
    """
    __tablename__ = 'expense_type'
    __table_args__ = default_table_args
    __mapper_args__ = dict(polymorphic_on="type",
                           polymorphic_identity="expense",
                           with_polymorphic='*')
    id = Column(Integer, primary_key=True)
    type = Column(String(30), nullable=False)
    label = Column(String(50))
    code = Column(String(15))


class ExpenseKmType(ExpenseType):
    """
        Type of expenses related to kilometric fees
    """
    __tablename__ = 'expensekm_type'
    __table_args__ = default_table_args
    __mapper_args__ = dict(polymorphic_identity='expensekm')
    id = Column(Integer, ForeignKey('expense_type.id'), primary_key=True)
    amount = Column(Float(precision=4))


class ExpenseTelType(ExpenseType):
    """
        Type of expenses related to telefonic fees
    """
    __tablename__ = 'expensetel_type'
    __table_args__ = default_table_args
    __mapper_args__ = dict(polymorphic_identity='expensetel')
    id = Column(Integer, ForeignKey('expense_type.id'), primary_key=True)
    percentage = Column(Integer)


class ExpenseSheet(DBBASE):
    """
        Model representing a whole ExpenseSheet
        An expensesheet is related to a company and an employee (one user may
        have multiple expense sheets if it has multiple companies)
        :param company_id: The user's company id
        :param user_id: The user's id
        :param year: The year the expense is related to
        :param month: The month the expense is related to
        :param status: Status of the sheet
        :param comments: Comments added to this expense sheet
        :param status_user: The user related to statuschange
        :param lines: expense lines of this sheet
    """
    __tablename__ = 'expense_sheet'
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    month = Column(Integer)
    year = Column(Integer)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="cascade"))
    user_id = Column(Integer, ForeignKey("accounts.id", ondelete="cascade"))
    status = Column(String(10))
    comments = Column(Text)
    status_user_id = Column(Integer, ForeignKey("accounts.id"))
    status_date = Column(Date(), default=date.today(), onupdate=date.today())
    company = relationship("Company",
            backref=backref("expenses",
                order_by="ExpenseSheet.month",
                cascade="all, delete-orphan"))
    user = relationship("User",
            primaryjoin="ExpenseSheet.user_id==User.id",
            backref=backref("expenses",
                order_by="ExpenseSheet.month",
                cascade="all, delete-orphan"))
    status_user = relationship("User",
            primaryjoin="ExpenseSheet.status_user_id==User.id")


class ExpenseLine(DBBASE):
    """
        Model representing an expense line
    """
    __tablename__ = 'expense_line'
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    date = Column(Date())
    category = Column(Enum([1, 2]))
    description = Column(String(255))
    ht = Column(Integer)
    tva = Column(Integer)
    code = Column(String(15))
    valid = Column(Boolean(), default=False)
    sheet_id = Column(Integer,
            ForeignKey("expense_sheet.id", ondelete="cascade"))
    sheet = relationship("ExpenseSheet",
                backref=backref("lines",
                    order_by="ExpenseLine.date",
                    cascade="all, delete-orphan"))
