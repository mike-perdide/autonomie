# -*- coding: utf-8 -*-
# * File Name :
#
# * Copyright (C) 2010 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 10-04-2012
# * Last Modified :
#
# * Project :
#
"""
    Usefull tools for building form schemas
"""
import os
import colander
import logging

from deform import widget
from deform_bootstrap.widget import ChosenSingleWidget
from autonomie.utils.fileupload import FileTempStore
from autonomie.utils.widgets import DisabledInput

log = logging.getLogger(__name__)

MAIL_ERROR_MESSAGE = u"Veuillez entrer une adresse mail valide"

def get_mail_input(missing=None):
    """
        Return a generic customized mail input field
    """
    return colander.SchemaNode(colander.String(),
                            title="Adresse e-mail",
                            validator=colander.Email(MAIL_ERROR_MESSAGE),
                            missing=missing
                            )

def deferred_upload_widget(path):
    @colander.deferred
    def configured_widget(node, kw):
        """
            returns a already pre-configured upload widget
        """
        session = kw['session']
        root_path = kw['rootpath']
        filepath = os.path.join(root_path, path)
        tmpstore = FileTempStore(session, filepath)
        return widget.FileUploadWidget(tmpstore)
    return configured_widget

@colander.deferred
def deferred_edit_widget(node, kw):
    """
        Dynamic assigned widget
        returns a text widget disabled if edit is True in schema binding
    """
    if kw.get('edit'):
        wid = DisabledInput()
    else:
        wid = widget.TextInputWidget()
    return wid

@colander.deferred
def deferred_autocomplete_widget(node, kw):
    """
        Dynamically assign a autocomplete single select widget
    """
    choices = kw.get('choices')
    if choices:
        wid = ChosenSingleWidget(values=choices)
    else:
        wid = widget.TextInputWidget()
    return wid
