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
    Tasks states
"""
import logging
import datetime

from autonomie.models.statemachine import StateMachine
from autonomie.exception import Forbidden
from autonomie.exception import SignatureError

log = logging.getLogger(__name__)

MANAGER_PERMS = "manage"

class TaskStates(StateMachine):
    """
        Task statemachine
    """
    status_attr = "CAEStatus"
    userid_attr = "statusPerson"


def valid_callback(task, **kw):
    """
        callback for the task validation
    """
    task = set_date(task)
    task.valid_callback()
    return task


def record_payment(task, **kw):
    """
        record a payment for the given task
        expecting a paymendMode to be passed throught kw
    """
    log.info(u"Recording a payment for {0}".format(task))
    if "mode" in kw and "amount" in kw:
        return task.record_payment(kw['mode'],
                                   kw['amount'],
                                   kw.get('resulted'))
    else:
        raise Forbidden()


def duplicate_task(task, **kw):
    """
        Duplicates a task
    """
    project = kw.get("project")
    phase = kw.get("phase")
    customer = kw.get('customer')
    if project is not None and phase is not None and customer is not None:
        return task.duplicate(kw['user'], project, phase, customer)
    else:
        raise Forbidden()


def phasechange_task(task, **kw):
    """
        Change a task's phase
    """
    phase = kw.get("phase")
    if phase is not None:
        task.phase = phase
        return task
    else:
        raise Forbidden()


def gen_cancelinvoice(task, **kw):
    """
        gen the cancelinvoice for the given task
    """
    if 'user' in kw:
        return task.gen_cancelinvoice(kw['user'])
    else:
        raise SignatureError()


def gen_invoices(task, **kw):
    """
        gen_invoices for the given task
    """
    if "user" in kw:
        return task.gen_invoices(kw['user'])
    else:
        raise SignatureError()


def set_date(task, **kw):
    """
        set the date of the current task
    """
    task.taskDate = datetime.date.today()
    return task


def set_financial_year(task, **kw):
    """
        Set the financial year of the current task
    """
    task.financial_year = kw['financial_year']
    return task

def set_products(task, **kw):
    """
        Set the products to the lines of the current task
    """
    for line in kw.get('lines', []):
        line_id = line.pop('id')
        product_id = line.get('product_id')
        if line_id is not None and product_id is not None:
            for line_ in task.lines:
                if line_.id == line_id:
                    line_.product_id = product_id
                else:
                    log.warning(u"Unknow line number in form validation : {0}"\
                            .format(line_id))
        else:
            log.warning(u"No line id was passed at form validation")
    return task


def get_base_state():
    """
        return the task states
    """
    result = {}
    result['draft'] = ('draft', 'wait', )
    result['invalid'] = ('draft', 'wait',)
    return result


def get_est_state():
    """
        return the estimation state workflow
        draft
        wait
        valid
        invalid
        aboest
    """
    duplicate = ('duplicate', 'view', duplicate_task, False,)
    phasechange = ("phasechange", "view", phasechange_task, False,)
    valid = ('valid', MANAGER_PERMS, set_date,)
    invalid = ('invalid', MANAGER_PERMS,)
    geninv = ('geninv', None, gen_invoices,)
    delete = ('delete', None, None, False,)
    result = {}
    result['draft'] = ('draft', 'wait', 'delete', valid)
    result['invalid'] = ('draft', 'wait', 'delete',)
    result['wait'] = (valid, invalid, duplicate, 'delete', phasechange)
    result['valid'] = ('aboest', geninv, duplicate, 'delete', phasechange)
    result['aboest'] = (delete, phasechange)
    result['geninv'] = (duplicate, phasechange)
    return result


def get_inv_state():
    """
        return the invoice state workflow
        draft
        wait
        valid
        invalid
        paid
        resulted
        aboinv
    """
    duplicate = ('duplicate', 'view', duplicate_task, False,)
    phasechange = ("phasechange", "view", phasechange_task, False,)
    valid = ('valid', MANAGER_PERMS, valid_callback,)
    invalid = ('invalid', MANAGER_PERMS,)
    aboinv = ('aboinv', MANAGER_PERMS,)
    paid = ('paid', MANAGER_PERMS, record_payment,)
    gencinv = ('gencinv', None, gen_cancelinvoice, False,)
    delete = ('delete', None, None, False,)
    mdelete = ('delete', MANAGER_PERMS, None, False,)
    resulted = ('resulted', MANAGER_PERMS,)
    financial_year = ('set_financial_year', MANAGER_PERMS, set_financial_year,
            False,)
    products = ("set_products", MANAGER_PERMS, set_products,
            False,)
    result = {}
    result['draft'] = ('draft', 'wait', delete, valid,)
    result['invalid'] = ('draft', 'wait', delete, )
    result['wait'] = (valid, invalid, duplicate, delete, financial_year,
            phasechange,)
    result['valid'] = (paid, resulted, gencinv, duplicate, mdelete,
            phasechange, financial_year, products,)
    result['paid'] = (paid, resulted, gencinv, duplicate, financial_year,
            phasechange, products, )
    result['resulted'] = (gencinv, duplicate, financial_year, phasechange,
            products,)
    result['aboinv'] = (delete, phasechange)
    return result


def get_cinv_state():
    """
        return the cancel invoice state workflow
        draft
        wait
        valid
        invalid
    """
    phasechange = ("phasechange", "view", phasechange_task, False,)
    valid = ('valid', MANAGER_PERMS, valid_callback,)
    invalid = ('invalid', MANAGER_PERMS,)
    financial_year = ('set_financial_year', MANAGER_PERMS, set_financial_year,
                        False,)
    products = ("set_products", MANAGER_PERMS, set_products,
            False,)
    result = {}
    result['draft'] = ('wait', 'delete', valid )
    result['wait'] = (valid, invalid, 'delete', financial_year, phasechange,
        products, )
    result['invalid'] = ('draft', 'wait', phasechange, products, )
    result['valid'] = (financial_year, phasechange, products, )
    return result

def get_maninv_state():
    """
        Return the states for manual invoices
    """
    return dict(valid=('resulted',))

DEFAULT_STATE_MACHINES = {
        "base": TaskStates('draft', get_base_state()),
        "estimation": TaskStates('draft', get_est_state()),
        "invoice": TaskStates('draft', get_inv_state()),
        "cancelinvoice": TaskStates('draft', get_cinv_state()),
        "manualinvoice":TaskStates("valid", get_maninv_state())}
