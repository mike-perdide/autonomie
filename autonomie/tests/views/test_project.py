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

from mock import MagicMock
from autonomie.models.project import Project
from autonomie.views.project import (ProjectAdd, ProjectEdit,
        project_addphase, project_archive, project_delete)

from autonomie.tests.base import BaseFunctionnalTest

APPSTRUCT = {'name':u'Projéct&$', "code":"ABDC", "customers":[]}

class Base(BaseFunctionnalTest):
    def addOne(self, appstruct=APPSTRUCT):
        self.config.add_route('project', '/')
        req = self.get_csrf_request()
        req.context = MagicMock(id=1)
        view = ProjectAdd(req)
        view.submit_success(appstruct)

    def getOne(self):
        try:
            return Project.query().filter(Project.name=="Projéct&$").one()
        except:
            return None

class TestProjectAdd(Base):
    def test_success(self):
        self.addOne()
        project = self.getOne()
        self.assertEqual(project.code, "ABDC")
        self.assertEqual(project.company_id, 1)

    def test_customer_not_exist(self):
        appstruct = {'name':u'Projéct&$', "code":"ABDC", "customers":["11111"]}
        self.addOne(appstruct)
        project = self.getOne()
        self.assertEqual(len(project.customers), 0)

    def test_customer(self):
        from autonomie.models.customer import Customer
        print Customer.get(1)
        appstruct = {'name':u'Projéct&$', "code":"ABDC", "customers":["1"]}
        self.addOne(appstruct)
        project = self.getOne()
        self.assertEqual(len(project.customers), 1)


class TestProjectEdit(Base):
    def test_edit(self):
        self.addOne()
        project = self.getOne()
        req = self.get_csrf_request()
        req.context = project
        appstruct = APPSTRUCT.copy()
        definition = u"Super project, should e ^dmeù*"
        appstruct['definition'] = definition
        view = ProjectEdit(req)
        view.submit_success(appstruct)
        project = self.getOne()
        self.assertEqual(project.definition, definition)

    def test_customer_remove(self):
        appstruct = {'name':u'Projéct&$', "code":"ABDC", "customers":["1"]}
        self.addOne(appstruct)
        project = self.getOne()
        req = self.get_csrf_request()
        req.context = project
        appstruct["customers"] = []
        view = ProjectEdit(req)
        view.submit_success(appstruct)
        project = self.getOne()
        self.assertEqual(len(project.customers), 0)

    def test_customer_add(self):
        self.addOne()
        project = self.getOne()
        req = self.get_csrf_request()
        req.context = project
        appstruct = APPSTRUCT.copy()
        appstruct['customers'] = ["1"]
        view = ProjectEdit(req)
        view.submit_success(appstruct)
        project = self.getOne()
        self.assertEqual(len(project.customers), 1)

class TestActions(Base):
    def test_delete(self):
        self.addOne()
        req = self.get_csrf_request()
        req.referer = "test"
        project = self.getOne()
        req.context = project
        project_delete(req)
        self.assertEqual(self.getOne(), None)

    def test_archive(self):
        self.addOne()
        req = self.get_csrf_request()
        req.referer = "test"
        project = self.getOne()
        req.context = project
        project_archive(req)
        self.assertEqual(self.getOne().archived, 1)

    def test_addphase(self):
        self.addOne()
        req = self.get_csrf_request()
        req.referer = "test"
        project = self.getOne()
        req.context = project
        req.params['phase'] = u'Phasé'
        project_addphase(req)
        self.assertEqual(len(self.getOne().phases), 2)
