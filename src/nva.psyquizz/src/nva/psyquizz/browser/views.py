# -*- coding: utf-8 -*-

import json
from ..apps import admin
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..interfaces import QuizzAlreadyCompleted
from ..models import IQuizz, Company, Course, Student, TrueOrFalse
from dolmen.menu import menuentry
from uvc.design.canvas import IContextualActionsMenu
<<<<<<< HEAD
from uvclight import Page
from uvclight import layer, title, name, context, get_template
from uvclight.auth import require
from zope.component import getUtilitiesFor
from cromlech.sqlalchemy import get_session
=======
from dolmen.menu import menuentry, order
from dolmen.location import get_absolute_url
from cromlech.browser import exceptions
from zope.cachedescriptors.property import CachedProperty
from zope.schema import getFieldsInOrder
from collections import OrderedDict
>>>>>>> 0ad39c6983b7b484f81d38da06ff84545b908fad


class QuizzErrorPage(Page):
    name('')
    context(QuizzAlreadyCompleted)
    require('zope.Public')

    def render(self):
<<<<<<< HEAD
        return _(u"This quizz is already completed and therefore closed.")
=======
        return u"This quizz is already completed and therefore closed."


class IPopulateCourse(Interface):
    
    nb_students = Int(
        title=u"Anzahl Fragebogen",
        required=True,
        )


@menuentry(IContextualActionsMenu, order=0)
class SchoolHomepage(Page):
    name('index')
    title('Startseite')
    context(admin.School)
    layer(IManagingRequest)
    require('manage.school')
    order(0)

    template = get_template('school.pt', __file__)


@menuentry(IContextualActionsMenu, order=0)
class SchoolCompanyHomepage(Page):
    name('index')
    title('Startseite')
    context(Company)
    layer(IManagingRequest)
    require('manage.school')
    
    template = get_template('company.pt', __file__)


@menuentry(IContextualActionsMenu, order=0)
class SchoolCourseHomepage(Page):
    name('index')
    title('Startseite')
    context(Course)
    layer(IManagingRequest)
    require('manage.school')

    template = get_template('course.pt', __file__)


@menuentry(IContextualActionsMenu, order=0)
class CompanyHomepage(Page):
    name('index')
    title('Startseite')
    context(Company)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('company.pt', __file__)


@menuentry(IContextualActionsMenu, order=0)
class CompanyCourseHomepage(Page):
    name('index')
    title('Startseite')
    context(Course)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('course.pt', __file__)
>>>>>>> 0ad39c6983b7b484f81d38da06ff84545b908fad


class QuizzStats(object):

    def __init__(self, total, completed, extra_questions, quizz):
        self.quizz = quizz.__schema__
        self.completed = list(completed)
        self.percent_base = len(self.completed)
        self.missing = total - self.percent_base 
        self.extra_questions = extra_questions

    @staticmethod
    def compute(forms, fields):
        questions = OrderedDict()
        extras = OrderedDict()

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

        for key, field in getFieldsInOrder(self.quizz):
            question = {
                'title': self.quizz[key].title,
                'description': self.quizz[key].description,
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
                'description': '',
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


@menuentry(IContextualActionsMenu, order=20)
class CompanyCourseResults(Page):
    name('results')
    context(Course)
    layer(ICompanyRequest)
    require('manage.company')
<<<<<<< HEAD
    title(_(u'Results for the course'))
=======
    title('Auswertung Unternehmensbereich')
>>>>>>> 0ad39c6983b7b484f81d38da06ff84545b908fad

    template = get_template('results.pt', __file__)

    def filters(self, query):
        return query

    def get_data(self):
        session = get_session('school')
        data = {}
        for name, quizz in getUtilitiesFor(IQuizz):
            students = session.query(Student).filter(
                Student.course_id == self.id).filter(
                    Student.company_id == self.context.name).filter(
                        Student.quizz_type == name).count()
            if students:
                answers = list(session.query(quizz).filter(
                    quizz.course_id == self.id).filter(
                        quizz.company_id == self.context.name))
                if answers:
                    data[name] = QuizzStats(
                        students, list(answers), self.extra_questions, quizz)
        return data

    def display(self):
        for name, result in self.get_data().items():
            yield name, result.get_answers()


@menuentry(IContextualActionsMenu, order=20)
class CompanyResults(CompanyCourseResults):
    name('results')
    context(Company)
    layer(ICompanyRequest)
    require('manage.company')
<<<<<<< HEAD
    title(_(u'Company wide results'))

    def get_data(self):
        session = get_session('school')
        data = {}
        for name, quizz in getUtilitiesFor(IQuizz):
            students = session.query(Student).filter(
                Student.company_id == self.context.name).filter(
                    Student.quizz_type == name).count()
=======
    title('Auswertung Unternehmen')

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


@menuentry(IContextualActionsMenu, order=10)
class CreateCompany(Form):
    context(admin.School)
    name('add.company')
    title(u'Unternehmen registrieren')
    title = u"Unternehmen registrieren"
    require('zope.Public')

    fields = Fields(ICompany).select('name', 'password')

    @property
    def action_url(self):
        return self.request.path

    @action(u'Registrieren')
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
        self.flash('Unternehmen erfolgreich registriert.')
        self.redirect('%s/%s' % (self.application_url(), company.name))
        return SUCCESS
>>>>>>> 0ad39c6983b7b484f81d38da06ff84545b908fad

            if students:
                answers = list(session.query(quizz).filter(
                    quizz.company_id == self.context.name))

<<<<<<< HEAD
                if answers:
                    courses = session.query(Course).filter(
                        Course.company_id == self.context.name).filter(
                            Course.quizz_type == name)
=======
@menuentry(IContextualActionsMenu, order=10)
class CreateCourse(Form):
    context(Company)
    name('add.course')
    require('manage.company')
    title(u'Unternehmensbereich hinzufügen')
>>>>>>> 0ad39c6983b7b484f81d38da06ff84545b908fad

                    extra_questions = "".join(
                        [course.extra_questions for course in courses])

                    data[name] = QuizzStats(
                        students, list(answers), extra_questions, quizz)
        return data

<<<<<<< HEAD
    def display(self):
        for name, result in self.get_data().items():
            yield name, result.get_answers()
=======
    @action(u'Anlegen')
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
        self.flash('Der Unternehemnsbereich wurde erfolgreich angelegt.')
        self.redirect('%s/%s' % (self.application_url(), course.id))
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class PopulateCourse(Form):
    context(Course)
    name('populate')
    require('zope.Public')
    title(u'Fragebogen anlegen')
>>>>>>> 0ad39c6983b7b484f81d38da06ff84545b908fad


@menuentry(IContextualActionsMenu, order=20)
class AllResults(CompanyCourseResults):
    name('results')
    context(admin.School)
    layer(ICompanyRequest)
    require('manage.school')
    title(_(u'Site wide results'))

<<<<<<< HEAD
    def update(self):
        session = get_session('school')
        data = {}
        for name, quizz in getUtilitiesFor(IQuizz):
            students = session.query(Student).filter(
                    Student.quizz_type == name).count()
            if students:
                answers = list(session.query(quizz))
=======
    @action(u'Anlegen')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash('An error occurred.')
            return
        session = get_session('school')
        for student in self.context.generate_students(data['nb_students']):
            self.context.append(student)
        self.flash('%s Fragebogen erfolgreich angelegt.' % data['nb_students'])
        return self.redirect(self.url(self.context))
>>>>>>> 0ad39c6983b7b484f81d38da06ff84545b908fad

                if answers:
                    courses = session.query(Course).filter(
                        Course.quizz_type == name)

<<<<<<< HEAD
                    extra_questions = "".join(
                        [course.extra_questions for course in courses])

                    data[name] = QuizzStats(
                        students, list(answers), extra_questions, quizz)
        return data

    def display(self):
        for name, result in self.get_data().items():
            yield name, result.get_answers()
=======
class IExtra(Interface):
    pass

IExtra.setTaggedValue('label', u'Zusatzfragen')


class AnswerQuizz(Form):
    context(Student)
    layer(IAnonymousRequest)
    name('index')
    require('zope.Public')
    title('Answer the quizz')
    dataValidators = []
    template = get_template('wizard.pt', __file__)

    @property
    def action_url(self):
        return '%s/%s' % (self.request.script_name, self.context.access)

    def updateWidgets(self):
        Form.updateWidgets(self)
        groups = OrderedDict()
        for widget in self.fieldWidgets:
            iface = widget.component.interface
	    if iface is None:
	        iface = IExtra
            group = groups.setdefault(iface, [])
            group.append(widget)
        self.groups = groups

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
	        extra_field.mode = 'radio'
                questions_fields.append(extra_field)
        
        return fields + Fields(*questions_fields)

    @action(u'Abschicken')
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


@menuentry(IContextualActionsMenu, order=20)
class AllResults(CompanyCourseResults):
    name('results')
    context(admin.School)
    layer(IManagingRequest)
    require('manage.school')
    title(u'Auswertung über alle Unternehmen')

    def update(self):
        total = 0
        extra_questions = ""
        completed = []
        for company in self.context:
            for course in company.courses:
                total += len(course._students)
                extra_questions += course.extra_questions
                completed += course.complete
        self.stats = QuizzStats(total, completed, extra_questions)

    def display(self):
        return self.stats.get_answers()

>>>>>>> 0ad39c6983b7b484f81d38da06ff84545b908fad
