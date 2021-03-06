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
    Template for estimation and invoice edition/creation
</%doc>
<%inherit file="/base.mako"></%inherit>
<%namespace file="/base/utils.mako" import="esc"/>
<%namespace file="/base/utils.mako" import="address"/>
<%block name='css'>
<link href="${request.static_url('autonomie:static/css/task.css')}" rel="stylesheet"  type="text/css" />
</%block>
<%block name='content'>
    <dl class="dl-horizontal">
        <dt>Prestataire</dt>
        <dd>${address(company, 'company')}</dd>
        </dl>
${form|n}
    <div style="display:none;" id='discount_popup'>
        <form id="discount_temp" class="form-horizontal">
            <div class="control-group">
                <div class="controls">
            <select id="discount_type_select">
                <option value="value" selected="true">En montant fixe</option>
                <option value="percent">En pourcentage</option>
            </select>
             </div>
         </div>
            <div class="control-group">
                <label class='control-label' for="discount_temp_description">Description</label>
                <div class="controls">
                    <textarea name="discount_temp_description" rows="2"></textarea>
                </div>
            </div>
            <div id='value_configuration'>
                <div class="control-group">
                    <label class='control-label' for="discount_temp_value">Montant</label>
                    <div class="controls">
                        <input type="text" name="discount_temp_value">
                    </div>
                </div>
                <div class="control-group">
                    <label class='control-label' for="discount_temp_tva">Tva</label>
                    <div class="controls">
                        <select name="discount_temp_tva" >
                            % for tva in tvas:
                                <option value="${tva.value}"
                                % if tva.default == 1:
                                    selected="on"
                                % endif
                                >${tva.name}</option>
                            % endfor
                        </select>
                    </div>
                </div>
            </div>
            <div id='percent_configuration' style='display:none'>
                <div class="control-group">
                    <label class='control-label' for="discount_temp_percent">Pourcentage</label>
                    <div class="controls">
                        <div class="input-append">
                            <!-- Important : ici le span et l'input sont sur la même ligne (les espaces font bugger le rendu -->
                            <input type="text" name="discount_temp_percent" class="span2" style="z-index:2500;"><span class="add-on">%</span>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        <div class='form-actions'>
            <button  class='btn btn-primary' type='button' onclick="discount.validate()">Valider</button>
            <button  class='btn btn-primary' type='button' onclick="discount.close()">Annuler</button>
        </div>
    </div>
    <script type='text/javascript'>
        $(function(){
            setPopUp('discount_popup', "Remise");
        });
    </script>
</%block>
<%block name="footerjs">
AppOptions = {};
AppOptions['loadurl'] = "${load_options_url}";
% if request.user.is_contractor():
    AppOptions['manager'] = false;
% else:
    AppOptions['manager'] = true;
% endif
</%block>

