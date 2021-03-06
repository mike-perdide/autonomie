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

<%inherit file="base.mako"></%inherit>
<%namespace file="base/utils.mako" import="format_text" />
<%block name='content'>
% if hasattr(project, "id") and project.id:
    <div class='row collapse' id='project-addphase'>
        <div class='span4 offset4'>
            <h3>Ajouter une phase</h3>
            <form class='navbar-form' method='POST' action="${request.route_path('project', id=project.id, _query=dict(action='addphase'))}">
                <input type='text' name='phase' />
                <button class='btn btn-primary' type='submit' name='submit' value='addphase'>Valider</button>
            </form>
            <br />
        </div>
    </div>
<div class='row collapse' id='project-description'>
        <div class="span8 offset2">
    <div class="well">
                    <h3>Client(s)</h3>
                    % for customer in project.customers:
                        <div class='well'>
                            <address>
                                ${format_text(customer.full_address)}
                            </address>
                        </div>
                    % endfor
        %if project.type:
            <b>Type de projet :</b> ${project.type}
        % endif
        <br />
        % if project.definition:
            <h3>Définition du projet</h3>
            ${project.definition}
        % endif
    </div>
</div>
</div>
% endif
<div class='row'>
    <div class='span6 offset3'>
        ${form|n}
    </div>
</div>
</%block>
