# -*- coding: utf-8 -*-

import transaction
import json
from cromlech.browser import redirect_response
from cromlech.webob.response import Response
from uvclight import Page, Form, Fields, SUCCESS, FAILURE
from uvclight import action, layer, name, context, title, get_template
from uvclight.auth import require
from ..apps import anonymous, company, admin
from ..models import Company, Student, Course
from ..models import IQuizz, ICourse, ICompany, TrueOrFalse
from ..interfaces import QuizzAlreadyCompleted
from ..interfaces import ICompanyRequest, IAnonymousRequest, IManagingRequest
from zope.interface import Interface
from zope.schema import Int, TextLine, Password, Choice
from cromlech.sqlalchemy import get_session
from uvc.design.canvas import IContextualActionsMenu
from dolmen.menu import menuentry
from dolmen.location import get_absolute_url
from cromlech.browser import exceptions
from zope.cachedescriptors.property import CachedProperty


class QuizzErrorPage(Page):
    name('')
    context(QuizzAlreadyCompleted)
    require('zope.Public')

    def render(self):
        return u"This quizz is already completed and therefore closed."


class IPopulateCourse(Interface):
    
    nb_students = Int(
        title=u"Number of students",
        required=True,
        )

    
class SchoolHomepage(Page):
    name('index')
    context(admin.School)
    layer(IManagingRequest)
    require('manage.school')

    template = get_template('school.pt', __file__)


class SchoolCompanyHomepage(Page):
    name('index')
    context(Company)
    layer(IManagingRequest)
    require('manage.school')
    
    template = get_template('company.pt', __file__)


class SchoolCourseHomepage(Page):
    name('index')
    context(Course)
    layer(IManagingRequest)
    require('manage.school')
    
    template = get_template('course.pt', __file__)


class CompanyHomepage(Page):
    name('index')
    context(Company)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('company.pt', __file__)


class CompanyCourseHomepage(Page):
    name('index')
    context(Course)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('course.pt', __file__)


class QuizzStats(object):

    quizz = IQuizz

    def __init__(self, total, completed, extra_questions):
        self.completed = list(completed)
        self.percent_base = len(self.completed)
        self.missing = total - self.percent_base 
        self.extra_questions = extra_questions

    @staticmethod
    def compute(forms, fields):
        questions = {}
        extras = {}

        for form in forms:
            for field in fields:
                question = questions.setdefault(field, {})
                answer = getattr(form, field)
                stat = question.setdefault(answer, 0)
                question[answer] = stat + 1
            
            xa = json.loads(form.extra_questions)
            for title, answer in xa.items():
                question = extras.setdefault(title, {})
                stat = question.setdefault(answer, 0)
                question[answer] = stat + 1

        return questions, extras

    def get_answers(self):
        computed, extras = self.compute(self.completed, list(self.quizz))

        for key in list(self.quizz):
            question = {
                'title': self.quizz[key].title,
                'answers': [],
                }
            for term in self.quizz[key].vocabulary:
                value = computed[key].get(term.value, 0)
                question['answers'].append({
                    'title': term.title,
                    'value': value,
                    'percent': float(value) / self.percent_base * 100
                    })
            yield question

        xq = set(self.extra_questions.strip().split('\n'))
        for title in xq:
            title = title.strip()
            if title == "":
                continue

            question = {
                'title': title,
                'answers': [],
                }
            for term in TrueOrFalse:
                value = extras[title].get(term.value, 0)
                question['answers'].append({
                    'title': term.title,
                    'value': value,
                    'percent': float(value) / self.percent_base * 100
                    })
            yield question


class CompanyCourseResults(Page):
    name('results')
    context(Course)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('results.pt', __file__)

    def update(self):
        total = len(self.context._students)
        extra_questions = self.context.extra_questions
        completed = self.context.complete
        self.stats = QuizzStats(total, completed, extra_questions)

    def display(self):
        return self.stats.get_answers()


class CompanyResults(CompanyCourseResults):
    name('results')
    context(Company)
    layer(ICompanyRequest)
    require('manage.company')

    def update(self):
        total = 0
        extra_questions = ""
        completed = []
        for course in self.context.courses:
            total += len(course._students)
            extra_questions += course.extra_questions
            completed += course.complete
        self.stats = QuizzStats(total, completed, extra_questions)

    def display(self):
        return self.stats.get_answers()
            

class StudentHomepage(Page):
    name('index')
    context(Student)
    require('zope.Public')
    
    quizz = IQuizz
    template = get_template('student.pt', __file__)


class QuizzHomepage(Page):
    name('index')
    context(anonymous.QuizzBoard)
    require('zope.Public')
    
    def __call__(self):
        raise exceptions.HTTPForbidden(self.context)


@menuentry(IContextualActionsMenu)
class CreateCompany(Form):
    context(admin.School)
    name('add.company')
    require('manage.school')
    title(u'Firma hinzufügen')
    title = u"Firma hinzufügen"

    fields = Fields(ICompany).select('name', 'password')

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
class CreateCourse(Form):
    context(Company)
    name('add.course')
    require('manage.company')
    title(u'Kurs hinzufügen')

    fields = Fields(ICourse).select('name', 'extra_questions')

    @property
    def action_url(self):
        return self.request.path

    @action(u'add')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash('An error occurred.')
            return FAILURE
        session = get_session('school')
        course = Course(**data)
        course.company_id = self.context.name
        session.add(course)
        session.flush()
        session.refresh(course)
        self.flash('Course added with success.')
        self.redirect('%s/%s' % (self.application_url(), course.id))
        return SUCCESS


@menuentry(IContextualActionsMenu)
class PopulateCourse(Form):
    context(Course)
    name('populate')
    require('zope.Public')
    title(u'Kennungen erzeugen')

    fields = Fields(IPopulateCourse)

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
            self.context.append(student)
        self.flash('Added %s accesses with success.' % data['nb_students'])
        return self.redirect(self.url(self.context))


class AnswerQuizz(Form):
    context(Student)
    layer(IAnonymousRequest)
    name('index')
    require('zope.Public')
    title('Answer the quizz')
    dataValidators = []
    
    @property
    def action_url(self):
        return '%s/%s' % (self.request.script_name, self.context.access)

    @property
    def fields(self):
        fields = Fields(IQuizz)

        for field in fields:
            field.mode = 'radio'

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
        
        return fields + Fields(*questions_fields)

    @action(u'Answer')
    def handle_save(self):
        print self.context.completion_date
        data, errors = self.extractData()
        if errors:
            self.flash(u'An error occurred.')
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
        self.context.complete_quizz(**data)
        session = get_session('school')
        session.add(self.context)
        self.flash(u'Thank you for answering the quizz')
        self.redirect(self.request.url)
        return SUCCESS
