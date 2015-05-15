# -*- coding: utf-8 -*-

import json
import uuid

from ..apps import admin
from ..i18n import _
from ..interfaces import IAnonymousRequest, ICompanyRequest
from ..models import Company, Student, Course, Criteria, ICriterias
from ..models import ICriteria, ICourse, ICompany, TrueOrFalse
from ..models import IQuizz, CriteriaAnswer
from collections import OrderedDict
from cromlech.sqlalchemy import get_session
from dolmen.menu import menuentry, order
from uvc.design.canvas import IContextualActionsMenu
from uvc.themes.dguv.resources import alldate
from dolmen.forms.base.markers import NO_VALUE
from uvclight import Form, EditForm, Fields, SUCCESS, FAILURE
from uvclight import action, layer, name, context, title, get_template
from uvclight.auth import require
from zope.component import getUtility
from zope.interface import Interface
from zope.schema import Int, Choice, Set
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class IExtraQuestions(Interface):
    pass


IExtraQuestions.setTaggedValue('label', 'Extra questions')


class IStudentFilters(Interface):
    pass


IStudentFilters.setTaggedValue('label', 'Getting started')


class IPopulateCourse(Interface):

    nb_students = Int(
        title=_(u"Number of students"),
        required=True,
        )


@menuentry(IContextualActionsMenu, order=10)
class CreateCriterias(Form):
    context(ICriterias)
    name('add.criteria')
    title(_(u'Add a criteria'))
    require('zope.Public')

    fields = Fields(ICriteria).select('title', 'items')

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
        criteria = Criteria(**data)
        criteria.company_id = self.context.__parent__.name
        session.add(criteria)
        session.flush()
        session.refresh(criteria)
        self.flash(_(u'Criteria added with success.'))
        self.redirect('%s' % self.application_url())
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class EditCriteria(EditForm):
    context(ICriteria)
    name('index')
    title(_(u'Edit criteria'))
    require('zope.Public')

    fields = Fields(ICriteria).select('title', 'items')

    @property
    def action_url(self):
        return self.request.path


@menuentry(IContextualActionsMenu, order=10)
class CreateCompany(Form):
    context(admin.School)
    name('add.company')
    title(_(u'Add a company'))
    require('zope.Public')

    fields = Fields(ICompany).select('name', 'password', 'mnr', 'email')

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
        company.activation = str(uuid.uuid1())
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

    fields = Fields(ICourse).select(
        'name', 'startdate', 'criterias',
        'quizz_type', 'extra_questions')

    def update(self):
        alldate.need()

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
class EditCourse(EditForm):
    context(Course)
    name('edit')
    require('manage.company')
    title(_(u'Edit the course'))

    fields = Fields(ICourse).select(
        'name', 'startdate')

    def update(self):
        alldate.need()

    @property
    def action_url(self):
        return self.request.path


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
        for student in self.context.generate_students(data['nb_students']):
            self.context.append(student)
        self.flash(_(u'Added ${nb} accesses with success.',
                     mapping=dict(nb=data['nb_students'])))
        return self.redirect(self.url(self.context))


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
            if widget.component.identifier.startswith('criteria_'):
                iface = IStudentFilters
            else:
                iface = widget.component.interface or IExtraQuestions
            group = groups.setdefault(iface, [])
            group.append(widget)
        self.groups = groups

    @property
    def fields(self):
        fields = Fields(self.quizz.__schema__)

        criteria_fields = []
        for criteria in self.context.course.criterias:
            values = [c.strip() for c in criteria.items.split('\n')
                      if c.strip()]

            criteria_field = Choice(
                __name__ = 'criteria_%s' % criteria.id,
                title=criteria.title,
                values=values,
                required=True,
            )
            criteria_fields.append(criteria_field)
        fields = Fields(*criteria_fields) + fields


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
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('school')

        fields = self.fields
        extra_answers = {}

        keys = data.keys()
        for key in keys:
            if key.startswith('criteria_'):
                cid = key.split('_', 1)[1]
                value = data.pop(key)
                field = fields.get(key)
                criteria_answer = CriteriaAnswer(
                    criteria_id=cid,
                    student_id=self.context.access,
                    answer=value,
                    )
                session.add(criteria_answer)
            elif key.startswith('extra_'):
                value = data.pop(key)
                field = fields.get(key)
                extra_answers[field.title] = value

        data['extra_questions'] = json.dumps(extra_answers)

        self.context.complete_quizz()
        quizz = self.quizz(**data)
        quizz.student_id = self.context.access
        quizz.company_id = self.context.company_id
        quizz.course_id = self.context.course_id

        session.add(self.context)
        session.add(quizz)
        self.flash(_(u'Thank you for answering the quizz'))
        self.redirect(self.request.url)
        return SUCCESS


def company_criterias(context):
    for criteria in context.criterias:
        vocabulary = SimpleVocabulary(
            [SimpleTerm(value=i.strip(), title=i.strip())
             for i in criteria.items.split('\n') if i.strip()])
        yield Set(
            __name__= '%i' % criteria.id,
            title=criteria.title,
            value_type=Choice(vocabulary=vocabulary),
            required=False)


@menuentry(IContextualActionsMenu, order=10)
class Stats(Form):
    context(Course)
    name('course.stats')
    title(_(u'Statistics'))
    require('manage.company')
    layer(ICompanyRequest)
    
    ignoreContent = True
    dataValidators = []
    criterias = {}
    
    @property
    def fields(self):
        return Fields(*list(company_criterias(self.context)))

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Filter'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        self.criterias = {int(k): v for k,v in data.items()
                          if v is not NO_VALUE}
        return SUCCESS



