<%doc>
Base template for task rendering
</%doc>
<%namespace file="/base/utils.mako" import="address" />
<%namespace file="/base/utils.mako" import="print_str_date" />
<%namespace file="/base/utils.mako" import="print_date" />
<%namespace file="/base/utils.mako" import="format_amount" />
<%namespace file="/base/utils.mako" import="format_quantity" />
<%namespace file="/base/utils.mako" import="format_text" />
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="shortcut icon" href="" type="image/x-icon" />
        <meta name="description" comment="">
        <meta name="KEYWORDS" CONTENT="">
        <meta NAME="ROBOTS" CONTENT="INDEX,FOLLOW,ALL">
        <link href="${request.static_url('autonomie:static/css/pdf.css', _app_url='')}" rel="stylesheet"  type="text/css" />
        <%block name='header'>
        </%block>
    </head>
    <body>
        <div class='header'>
            <img src='/assets/${company.get_header_filepath()}' alt='${company.name}' width='100%'/>
        </div>
        <div class='row'>
            <div class='addressblock'>
                ${print_str_date(task.taskDate)}
                <br />
                ${address(project.client, 'client')}
            </div>
        </div>
        <div class="informationblock">
        <%block name='information'>
        </%block>
        </div>
        %if task.displayedUnits == 1:
            <% colspan = 2 %>
        %else:
            <% colspan = 1 %>
        % endif
        <div class='row'>
        <table class="lines span12">
            <thead>
                <tr>
                    <th class="description">Intitulé des postes</th>
                    %if task.displayedUnits == 1:
                        <th class="quantity">P.U. x Qté</th>
                    % endif
                    <th class="price">Prix</th>
                </tr>
            </thead>
            <tbody>
                % for line in task.lines:
                    <tr>
                        <td class="description">${format_text(line.description)}</td>
                        %if task.displayedUnits == 1:
                            <td class="quantity">${format_amount(line.cost)}&nbsp;€&nbsp;x&nbsp;${format_quantity(line.quantity)} ${line.get_unity_label(pretty=True)}</td>
                        % endif
                        <td class="price">${format_amount(line.total(), trim=False)}&nbsp;€</td>
                    </tr>
                % endfor
                <tr>
                    <td colspan='${colspan}' class='rightalign'>
                        Total HT
                    </td>
                    <td class='price'>
                        ${format_amount(task.lines_total(), trim=False)}&nbsp;€
                     </td>
                 </tr>
                 %if hasattr(task, "discountHT") and task.discountHT:
                    <tr>
                        <td colspan='${colspan}' class='rightalign'>
                            Remise commerciale
                        </td>
                        <td class='price'>
                            ${format_amount(task.discountHT)}&nbsp;€
                        </td>
                    </tr>
                    <tr>
                        <td colspan='${colspan}' class='rightalign'>
                         Total HT après remise
                        </td>
                        <td class='price'>
                            ${format_amount(task.total_ht())}&nbsp;€
                        </td>
                    </tr>

                % endif
                % if task.tva<0:
                    <tr>
                        <td colspan='${colspan + 1}'class='rightalign'>
                            TVA non applicable selon l'article 259b du CGI.
                        </td>
                    </tr>
                % else:
                    <tr>
                        <td colspan='${colspan}' class='rightalign'>
                            TVA (${format_amount(task.tva)} %)
                        </td>
                        <td class='price'>
                            ${format_amount(task.tva_amount())}&nbsp;€
                        </td>
                    </tr>
                % endif
                %if task.expenses:
                    <tr>
                        <td colspan='${colspan}' class='rightalign'>
                            Frais liés à la prestation
                        </td>
                        <td class='price'>
                            ${format_amount(task.expenses_amount())}&nbsp;€
                        </td>
                    </tr>
                %endif
                <tr>
                    <td colspan='${colspan}' class='rightalign'>
                        Total TTC
                    </td>
                    <td class='price'>
                        ${format_amount(task.total())}&nbsp;€
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <%block name="notes_and_conditions">
        ## All infos beetween document lines and footer text (notes, payment conditions ...)
    </%block>

        <div id="footer">
            % if config.has_key('coop_pdffootertitle'):
                <b>${format_text(config.get('coop_pdffootertitle'))}</b><br />
            %endif
            % if hasattr(task, "course") and task.course == 1 and config.has_key('coop_pdffootercourse'):
                ${format_text(config.get('coop_pdffootercourse'))}<br />
            % endif
            % if config.has_key('coop_pdffootertext'):
                ${format_text(config.get('coop_pdffootertext'))}
            % endif
        </div>
    </body>
</html>
