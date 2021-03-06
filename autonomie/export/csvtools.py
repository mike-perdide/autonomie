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
    Csv exporter for sqlalchemy datas

    uses the sqlalchemy info attr to retrieve meta datas about the columns
"""
import csv
import cStringIO as StringIO
from autonomie.utils.sqla import get_columns
from autonomie.utils.ascii import (
        force_ascii,
        force_utf8,
        )


CSV_DELIMITER = ';'
CSV_QUOTECHAR = '"'


def get_column_label(column):
    """
        Return the label of a column
    """
    return column.info.get('label', column.name)


def should_be_exported(column):
    """
        Check if the column should be part of the export
        Default True
        Add info['options']['csv_exclude'] to avoid the export of the given
        field
    """
    return not column.info.get('options', {}).has_key('csv_exclude')


def collect_labels(model):
    """
        collect the column labels our dest file is supposed to provide
    """
    for column in get_columns(model):
        if should_be_exported(column):
            yield get_column_label(column)


def collect_keys(model):
    """
        Return the different column keys
    """
    for column in get_columns(model):
        if should_be_exported(column):
            yield column.name


class BaseCsvWriter(object):
    keys = []
    delimiter = CSV_DELIMITER
    quotechar = CSV_QUOTECHAR

    def __init__(self, datas=None):
        self._datas = []
        if datas is not None:
            for data in datas:
                self.add_row(data)

    @staticmethod
    def format_row(row):
        return row

    def add_row(self, row):
        """
            Add a row to our buffer
        """
        self._datas.append(self.format_row(row))

    def render(self):
        """
            Write to the dest buffer
        """
        f_buf = StringIO.StringIO()
        outfile = csv.DictWriter(f_buf,
                                 self.keys,
                                 delimiter=self.delimiter,
                                 quotechar=self.quotechar,
                                 quoting=csv.QUOTE_ALL)
        outfile.writeheader()
        outfile.writerows(self._datas)
        return f_buf


class SqlaToCsvWriter(BaseCsvWriter):
    """
        Render a sqla model as a csv file buffer
        :param model: our model class
    """
    def __init__(self, model):
        super(SqlaToCsvWriter, self).__init__()
        self.model = model
        self.keys = list(collect_keys(self.model))

    def format_row(self, row):
        """
            restrict the dictionnary to the current fieldnames
        """
        ret = {}
        for key, value in row.items():
            if key in self.keys:
                ret[key] = force_utf8(value)
        return ret
