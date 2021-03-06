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
    Manage view :
        - last documents page
"""
import logging

from sqlalchemy import and_

from autonomie.models.task.task import Task
from autonomie.models.treasury import ExpenseSheet
from autonomie.models.task.invoice import Invoice
from autonomie.models.task.invoice import CancelInvoice
from autonomie.models.task.estimation import Estimation
from autonomie.models.project import Phase

log = logging.getLogger(__name__)


def manage(request):
    """
        The manage view
    """
    documents = Task.query()\
            .with_polymorphic([Invoice, CancelInvoice, Estimation])\
            .join(Task.phase)\
            .filter(and_(Task.CAEStatus == 'wait', Phase.name is not None))\
            .order_by(Task.statusDate).all()
    for document in documents:
        document.url = request.route_path(document.type_, id=document.id)

    expenses = ExpenseSheet.query()\
            .filter(ExpenseSheet.status == 'wait')\
            .order_by(ExpenseSheet.month).all()
    for expense in expenses:
        expense.url = request.route_path("expense", id=expense.id)
    return dict(title=u"Documents en attente de validation",
                tasks=documents,
                expenses = expenses)

def includeme(config):
    config.add_route("manage",
                    "/manage")
    config.add_view(manage,
                    route_name="manage",
                    renderer="manage.mako",
                    permission="manage")
