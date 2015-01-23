# -*- coding: utf-8 -*-

import transaction
from cromlech.browser import redirect_response
from cromlech.webob.response import Response
from uvclight import Page, Form, Fields, SUCCESS, FAILURE
from uvclight import action, layer, name, context, title, get_template
from uvclight.auth import require
from ..wsgi import School, QuizzBoard, QuizzAlreadyCompleted
from ..models import Company, Student, IQuizz
from ..interfaces import IAnonymousRequest, IManagingRequest
from zope.interface import Interface
from zope.schema import Int, TextLine
from cromlech.sqlalchemy import get_session
from uvc.design.canvas import IContextualActionsMenu
from dolmen.menu import menuentry
from dolmen.location import get_absolute_url
from cromlech.browser import exceptions


class QuizzErrorPage(Page):
    name('')
    context(QuizzAlreadyCompleted)
    require('zope.Public')

    def render(self):
        return u"This quizz is already completed and therefore closed."


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


class StudentHomepage(Page):
    name('index')
    context(Student)
    layer(IManagingRequest)
    require('zope.Public')
    
    quizz = IQuizz
    template = get_template('student.pt', __file__)


class QuizzHomepage(Page):
    name('index')
    context(QuizzBoard)
    require('zope.Public')
    
    def __call__(self):
        raise exceptions.HTTPForbidden(self.context)


@menuentry(IContextualActionsMenu)
class CreateCompany(Form):
    context(School)
    name('add.company')
    require('manage.school')
    title('Add a company')

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
    context(Company)
    name('populate')
    require('zope.Public')
    title('Add accesses')

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


class AnswerQuizz(Form):
    context(Student)
    layer(IAnonymousRequest)
    name('index')
    require('zope.Public')
    title('Answer the quizz')

    fields = Fields(IQuizz)

    for field in fields:
        field.mode = 'radio'

    @property
    def action_url(self):
        return '%s/%s' % (self.request.script_name, self.context.access)

    @action(u'Answer')
    def handle_save(self):
        print self.context.completion_date
        data, errors = self.extractData()
        if errors:
            self.flash(u'An error occurred.')
            return FAILURE
        self.context.complete_quizz(**data)
        session = get_session('school')
        session.add(self.context)
        self.flash(u'Thank you for answering the quizz')
        self.redirect(self.request.url)
        return SUCCESS
