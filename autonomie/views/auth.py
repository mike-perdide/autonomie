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
    All Authentication views
"""
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden

from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import remember
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.threadlocal import get_current_registry

from deform import Form
from deform import Button
from deform import ValidationFailure

from autonomie.views.forms.user import get_auth_schema

log = logging.getLogger(__name__)


def forbidden_view(request):
    """
        The forbidden view (handles the redirection to login form)
    """
    log.debug("We are in a forbidden view")
    login = authenticated_userid(request)
    if login:
        log.warn(u"An access has been forbidden to '{0}'".format(login))
        redirect = HTTPForbidden()
    else:
        log.debug(u"An access has been forbidden to an unauthenticated user")
        #redirecting to the login page with the current path as param
        loc = request.route_url('login', _query=(('nextpage', request.path),))
        if request.is_xhr:
            redirect = dict(redirect=loc)
        else:
            redirect = HTTPFound(location=loc)
    return redirect


def get_longtimeout():
    settings = get_current_registry().settings
    default = 3600
    longtimeout = settings.get("session.longtimeout", default)
    try:
        longtimeout = int(longtimeout)
    except:
        longtimeout = default
    return longtimeout


def login_view(request):
    """
        The login view
    """
    form = Form(get_auth_schema(),
                buttons=(Button(name="submit",
                                title="Connexion",
                                type='submit'),))
    nextpage = request.params.get('nextpage') or request.route_url('index')
    # avoid redirection looping
    if nextpage == request.route_url('login'):
        nextpage = request.route_url('index')
    app_struct = {'nextpage': nextpage}
    myform = form.render(app_struct)
    fail_message = None
    if 'submit' in request.params:
        controls = request.params.items()
        log.info(u"Authenticating : '{0}'".format(request.params.get('login')))
        try:
            datas = form.validate(controls)
        except ValidationFailure, err:
            log.exception(u" - Authentication error")
            myform = err.render()
            fail_message = u"Erreur d'authentification"
            return {'title': "Authentification",
                    'html_form': myform,
                    'message': fail_message
                    }
        else:
            login = datas['login']
            log.info(u" + '{0}' has been authenticated".format(login))
            # Storing the datas in the request object
            remember(request, login)
            remember_me = datas.get('remember_me', False)
            response = HTTPFound(location=nextpage)
            if remember_me:
                log.debug("  * The user wants to be remembered")
                longtimeout = get_longtimeout()
                response.set_cookie('remember_me', "ok", max_age=longtimeout)
            return response
    return {
            'title': "Bienvenue dans Autonomie",
            'html_form': myform,
            'message': fail_message
            }


def logout_view(request):
    """
        The logout view
    """
    loc = request.route_url('index')
    headers = forget(request)
    response = HTTPFound(location=loc, headers=headers)
    response.delete_cookie("remember_me")
    return response


def includeme(config):
    """
        Add auth related routes/views
    """
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_view(forbidden_view,
                    context=HTTPForbidden,
                    permission=NO_PERMISSION_REQUIRED,
                    xhr=True,
                    renderer='json')
    config.add_view(forbidden_view,
                    context=HTTPForbidden,
                    permission=NO_PERMISSION_REQUIRED)
    config.add_view(logout_view,
                    route_name='logout',
                    permission=NO_PERMISSION_REQUIRED)
    config.add_view(login_view,
                    route_name='login',
                    permission=NO_PERMISSION_REQUIRED,
                    renderer='login.mako')
