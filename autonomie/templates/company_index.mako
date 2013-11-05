<%doc>
 * Copyright (C) 2012-2013 Croissance Commune
 * Authors:
       * Arezki Feth <f.a@majerti.fr>;
       * Miotte Julien <j.m@majerti.fr>;
       * Pettier Gabriel;
       * TJEBBES Gaston <g.t@majerti.fr>

 This file is part of Autonomie : Progiciel de gestion de CAE.

    Autonomie is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Autonomie is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Autonomie.  If not, see <http://www.gnu.org/licenses/>.
</%doc>

<%doc>
    Company index page shows last activities and elapsed invoices
</%doc>
<%inherit file="base.mako"></%inherit>
<%block name='content'>
<div class='row'>
    <div class='span4'>
        %if elapsed_invoices:
            <div class='well' style="margin-top:10px">
                <div class='section-header'>
                    Vos impayés de + de 45 jours
                </div>
                <table class='table table-stripped'>
                    <thead>
                        <th>Numéro</th>
                        <th>Client</th>
                        <th>Total</th>
                        <th></th>
                    </thead>
                    <tbody>
                        % for invoice in elapsed_invoices[:5]:
                            <tr>
                                <td>
                                    ${request.config.get('invoiceprefix')}${invoice.officialNumber}
                                </td>
                                <td>
                                    ${format_customer(invoice.customer)}
                                </td>
                                <td>
                                    ${api.format_amount(invoice.total())|n}&nbsp;€
                                </td>
                                <td>
                                    ${table_btn(request.route_path("invoice", id=invoice.id), u"Voir", u"Voir ce document", icon=u"icon-search")}
                                </td>
                            </tr>
                        % endfor
                    </tbody>
                </table>
                % if len(elapsed_invoices) > 5:
                    <b>...</b>
                    <a class='btn btn-primary'
                        href="${request.route_path('company_invoices', id=company.id, _query=dict(paid="notpaid"))}">
                        Voir plus
                    </a>
                % else:
                    <a class='btn btn-primary'
                        href="${request.route_path('company_invoices', id=company.id, _query=dict(paid="notpaid"))}">
                        Voir
                    </a>
                % endif
            </div>
        %endif
    </div>
    <div class='span6 offset1'>
        % if request.config.has_key('welcome'):
            <p>
                ${format_text(request.config['welcome'])}
            </p>
        % endif
    </div>
</div>

${request.layout_manager.render_panel('company_tasks')}
</%block>
