# -*- coding: utf-8 -*-

import json
from ..models import IQuizz
from ..apps import admin
from ..i18n import _
from ..interfaces import IAnonymousRequest
from ..models import Company, Student, Course
from ..models import ICourse, ICompany, TrueOrFalse
from cromlech.sqlalchemy import get_session
from dolmen.menu import menuentry, order
from uvc.design.canvas import IContextualActionsMenu
from uvclight import JSON, Form, Fields, SUCCESS, FAILURE
from uvclight import action, layer, name, context, title, get_template
from uvclight.auth import require
from zope.interface import Interface
from zope.component import getUtility
from zope.schema import Int, Choice


class IExtraQuestions(Interface):
    pass


IExtraQuestions.setTaggedValue('label', 'Extra questions')


class IPopulateCourse(Interface):
    
    nb_students = Int(
        title=_(u"Number of students"),
        required=True,
        )


@menuentry(IContextualActionsMenu, order=10)
class CreateCompany(Form):
    context(admin.School)
    name('add.company')
    title(_(u'Add a company'))
    require('zope.Public')

    fields = Fields(ICompany).select('name', 'password')

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE
        if data['name'] in self.context:
            self.flash(_(u'Name ${name} already exists.',
                         mapping=dict(name=data['name'])))
            return FAILURE
        session = get_session('school')
        company = Company(**data)
        session.add(company)
        session.flush()
        session.refresh(company)
        self.flash(_(u'Company added with success.'))
        self.redirect('%s/%s' % (self.application_url(), company.name))
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class CreateCourse(Form):
    context(Company)
    name('add.course')
    require('manage.company')
    title(_(u'Add a course'))

    fields = Fields(ICourse).select('name', 'quizz_type', 'extra_questions')

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE
        session = get_session('school')
        course = Course(**data)
        course.company_id = self.context.name
        session.add(course)
        session.flush()
        session.refresh(course)
        self.flash(_(u'Course added with success.'))
        self.redirect('%s/%s' % (self.application_url(), course.id))
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class PopulateCourse(Form):
    context(Course)
    name('populate')
    require('zope.Public')
    title(_(u'Add accesses'))
    order(3)

    fields = Fields(IPopulateCourse)

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Populate'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return
        session = get_session('school')
        for student in self.context.generate_students(data['nb_students']):
            self.context.append(student)
        self.flash(_(u'Added ${nb} accesses with success.',
                     mapping=dict(nb=data['nb_students'])))
        return self.redirect(self.url(self.context))


from collections import OrderedDict


class AnswerQuizz(Form):
    context(Student)
    layer(IAnonymousRequest)
    name('index')
    require('zope.Public')
    title(_(u'Answer the quizz'))
    dataValidators = []
    template = get_template('wizard.pt', __file__)

    def update(self):
        course = self.context.course
        self.quizz = getUtility(IQuizz, name=course.quizz_type)
        Form.update(self)

    @property
    def action_url(self):
        return '%s/%s' % (self.request.script_name, self.context.access)

    def updateWidgets(self):
        Form.updateWidgets(self)
        groups = OrderedDict()
        for widget in self.fieldWidgets:
            iface = widget.component.interface or IExtraQuestions
            group = groups.setdefault(iface, [])
            group.append(widget)
        self.groups = groups

    @property
    def fields(self):

        fields = Fields(self.quizz.__schema__)
        questions_text = self.context.course.extra_questions
        questions_fields = []
        if questions_text:
            questions = questions_text.strip().split('\n')
            for idx, question in enumerate(questions, 1):
                question = question.decode('utf-8').strip()
                extra_field = Choice(
                    __name__ = 'extra_question%s' % idx,
                    title=question,
                    vocabulary=TrueOrFalse,
                    required=True,
                    )
                questions_fields.append(extra_field)
        
        fields += Fields(*questions_fields)
        for field in fields:
            field.mode = 'radio'
        return fields


    @action(_(u'Answer'))
    def handle_save(self):
        print self.context.completion_date
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        fields = self.fields
        extra_answers = {}
        keys = data.keys()
        for key in keys:
            if key.startswith('extra_'):
                value = data.pop(key)
                field = fields.get(key)
                extra_answers[field.title] = value
        
        data['extra_questions'] = json.dumps(extra_answers)
        
        self.context.complete_quizz()
        quizz = self.quizz(**data)
        quizz.student_id = self.context.access
        quizz.company_id = self.context.company_id
        quizz.course_id = self.context.course_id

        session = get_session('school')
        session.add(self.context)
        session.add(quizz)
        self.flash(_(u'Thank you for answering the quizz'))
        self.redirect(self.request.url)
        return SUCCESS
