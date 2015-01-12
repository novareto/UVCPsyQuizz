# -*- coding: utf-8 -*-

from cromlech.browser import redirect_response
from cromlech.webob.response import Response
from uvclight import Page, Form, Fields, SUCCESS, FAILURE
from uvclight import action, name, context, get_template
from uvclight.auth import require
from ..wsgi import School
from ..models.course import Company, Student
from zope.interface import Interface
from zope.schema import Int, TextLine
from cromlech.sqlalchemy import get_session
from uvc.design.canvas import IContextualActionsMenu
from dolmen.menu import menuentry
from dolmen.location import get_absolute_url


class ICreateCompany(Interface):

    name = TextLine(
        title=u"Company name",
        required=True,
        )
    
    password = TextLine(
        title=u"Password for observation access",
        required=True,
        )
    

class IPopulateCompany(Interface):
    
    nb_students = Int(
        title=u"Number of students",
        required=True,
        )

    
class SchoolHomepage(Page):
    name('index')
    context(School)
    require('manage.school')
    
    template = get_template('school.pt', __file__)


class CompanyHomepage(Page):
    name('index')
    context(Company)
    require('zope.Public')
    
    template = get_template('company.pt', __file__)


@menuentry(IContextualActionsMenu)
class CreateCompany(Form):
    name('add.company')
    context(School)
    require('manage.school')
    
    fields = Fields(ICreateCompany)

    @property
    def action_url(self):
        return self.request.path

    @action(u'add')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash('An error occurred.')
            return FAILURE
        if data['name'] in self.context:
            self.flash('Name %r already exists.' % data['name'])
            return FAILURE
        session = get_session('school')
        company = Company(**data)
        session.add(company)
        session.flush()
        session.refresh(company)
        self.flash('Company added with success.')
        self.redirect('%s/%s' % (self.application_url(), company.name))
        return SUCCESS

    
@menuentry(IContextualActionsMenu)
class PopulateCompany(Form):
    name('populate')
    context(Company)
    require('zope.Public')

    fields = Fields(IPopulateCompany)

    @property
    def action_url(self):
        return self.request.path

    @action(u'Populate')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash('An error occurred.')
            return
        session = get_session('school')
        for student in self.context.generate_students(data['nb_students']):
            self.context.students.append(student)
        self.flash('Added %s accesses with success.' % data['nb_students'])
        return self.redirect(self.url(self.context))
