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
    estimation template
</%doc>
<%inherit file="/tasks/task.mako" />
<%namespace file="/base/utils.mako" import="format_text" />
<%def name="table(title, datas)">
    <div class="title">
        ${title}
    </div>
    <div class='content'>
        ${format_text(datas)}
    </div>
</%def>
<%block name='header'>
<style>
    @page {
        size: a4 portrait;
        margin:1cm;
        margin-bottom:3.5cm;
        % if not task.has_been_validated() and not task.is_cancelled():
            background-image: url("${request.static_url('autonomie:static/watermark_estimation.jpg', _app_url='')}");
        % endif
        @frame footer{
            -pdf-frame-content: footer;
            bottom: 0cm;
            margin-left: 1cm;
            margin-right: 1cm;
            % if hasattr(task, "course") and task.course == 1 and config.has_key('coop_pdffootercourse'):
                height: 4cm;
            % else:
                height:3cm;
            % endif

            }
    }
</style>
</%block>
<%block name="information">
<strong>DEVIS N° </strong>${task.number}<br />
<strong>Objet : </strong>${format_text(task.description)}<br />
% if config.has_key('coop_estimationheader'):
    ${format_text(config['coop_estimationheader'])}
% endif
</%block>
<%block name="notes_and_conditions">
%if task.exclusions:
    ${table(u"Notes", task.exclusions)}
%endif
% if task.paymentDisplay != u"NONE":
    % if task.paymentDisplay == u"ALL":
        <% colspan = 3 %>
    %else:
        <% colspan = 1 %>
    % endif
    <div class='row'>
        <table class='lines span12'>
            <thead>
                <th colspan='${colspan}' style='text-align:left'>Conditions de paiement</th>
            </thead>
            <tbody>
                <tr>
                    <td colspan='${colspan}'>
                        ${task.paymentConditions}
                        <br />
                        % if task.deposit > 0 :
                            Un acompte, puis paiement en ${task.get_nb_payment_lines()} fois.
                        %else:
                            Paiement en ${task.get_nb_payment_lines()} fois.
                        %endif
                    </td>
                </tr>
                % if task.paymentDisplay == u"ALL":
                    ## l'utilisateur a demandé le détail du paiement
                    ## L'acompte à la commande
                    % if task.deposit > 0 :
                        <tr>
                            <td>Acompte</td>
                            <td>à la commande</td>
                            <td class='price'>${api.format_amount(task.deposit_amount_ttc())|n}&nbsp;€</td>
                        </tr>
                    % endif
                    ## Les paiements intermédiaires
                    % for line in task.payment_lines[:-1]:
                        <tr>
                            <td>${api.format_date(line.paymentDate)}</td>
                            <td>${line.description}</td>
                            %if task.manualDeliverables == 1:
                                <td>${api.format_amount(line.amount)|n}&nbsp;€</td>
                            %else:
                                <td class='price'>${api.format_amount(task.paymentline_amount_ttc())|n}&nbsp;€</td>
                            %endif
                        </tr>
                    % endfor
                    ## On affiche le solde qui doit être calculé séparément pour être sûr de tomber juste
                    <tr>
                        <td>
                            ${api.format_date(task.payment_lines[-1].paymentDate)}
                        </td>
                        <td>
                            ${format_text(task.payment_lines[-1].description)}
                        </td>
                        <td class='price'>
                            ${api.format_amount(task.sold())|n}&nbsp;€
                        </td>
                    </tr>
                % endif
            </tbody>
        </table>
</div>
%else:
    %if task.paymentConditions:
        ${table(u"Conditions de paiement", task.paymentConditions)}
    % endif
% endif
% if config.has_key('coop_estimationfooter'):
<div class='row'>
    ${table(u"Acceptation du devis", config.get('coop_estimationfooter'))}
</div>
%endif
</%block>
