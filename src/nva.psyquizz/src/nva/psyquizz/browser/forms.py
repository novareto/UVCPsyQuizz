# -*- coding: utf-8 -*-

import os
import json
import uuid
import uvclight
import html2text

from .. import wysiwyg
from ..i18n import _
from ..interfaces import IAnonymousRequest, ICompanyRequest, IRegistrationRequest
from ..models import Account, Company, Course, ClassSession, Student
from ..models import ICourseSession, IAccount, ICompany, ICourse, IClassSession
from ..models import ICompanyTransfer, ICompanies, IQuizz, TrueOrFalse
from ..models import Criteria, CriteriaAnswer, ICriteria, ICriterias
from .emailer import SecureMailer, prepare, ENCODING

from collections import OrderedDict
from cromlech.sqlalchemy import get_session
from dolmen.forms.base.markers import NO_VALUE
from dolmen.forms.base.errors import Error
from dolmen.forms.base import makeAdaptiveDataManager
from dolmen.menu import menuentry, order
from string import Template
from uvc.design.canvas import IContextualActionsMenu, IPersonalMenu
from uvc.design.canvas import IDocumentActions
from uvclight.form_components.fields import Captcha
from uvclight import Form, EditForm, DeleteForm, Fields, SUCCESS, FAILURE
from uvclight import action, layer, name, title, get_template, baseclass
from uvclight.auth import require
from zope.component import getUtility
from zope.interface import Interface
from zope.schema import Int, Choice, Set, Password
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from grokcore.component import baseclass, Adapter, provides, context
from siguvtheme.resources import all_dates, datepicker_de


with open(os.path.join(os.path.dirname(__file__), 'mail.tpl'), 'r') as fd:
    data = unicode(fd.read(), 'utf-8')
    mail_template = Template(data.encode(ENCODING))


def send_activation_code(company_name, email, code, base_url):
    #mailer = SecureMailer('localhost')
    mailer = SecureMailer('smtprelay.bg10.bgfe.local')
    from_ = 'extranet@bgetem.de'
    title = u'Aktivierung der Online-Hilfe zur Gefährdungsbeurteilung psychischer Belastung'.encode(ENCODING)
    with mailer as sender:
        html = mail_template.substitute(
            title=title,
            encoding=ENCODING,
            base_url=base_url,
            email=email.encode(ENCODING),
            company=company_name.encode(ENCODING),
            activation_code=code)

        text = html2text.html2text(html.decode('utf-8'))
        mail = prepare(from_, email, title, html, text.encode('utf-8'))
        print mail.as_string()
        #sender(from_, email, mail.as_string())
    return True


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
        criteria.company_id = self.context.__parent__.id
        session.add(criteria)
        session.flush()
        session.refresh(criteria)
        self.flash(_(u'Criteria added with success.'))
        self.redirect(self.url(self.context))
        return SUCCESS


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
class AddSession(Form):
    context(ICourse)
    name('add.session')
    title(_(u'Add a session'))
    require('zope.Public')

    fields = Fields(IClassSession).select('startdate', 'duration', 'about')

    def update(self):
        all_dates.need()
        datepicker_de.need()
        wysiwyg.need()
        Form.update(self)

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
        clssession = ClassSession(**data)
        clssession.course_id = self.context.id
        clssession.company_id = self.context.__parent__.id
        session.add(clssession)
        session.flush()
        session.refresh(clssession)
        self.flash(_(u'Session added with success.'))
        self.redirect('%s' % self.url(self.context))
        return SUCCESS


class ICaptched(Interface):

    captcha = Captcha(
        title=u'Captcha',
        required=True)


class IVerifyPassword(Interface):

    verif = Password(
        title=_(u'Retype password'),
        required=True)


@menuentry(IContextualActionsMenu, order=10)
class CreateAccount(Form):
    name('index')
    layer(IRegistrationRequest)
    title(_(u'Add an account'))
    require('zope.Public')

    dataValidators = []
    fields = (Fields(IAccount).select('name', 'email', 'password') +
              Fields(IVerifyPassword, ICaptched))

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        session = get_session('school')

        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        if not data['password'] == data['verif']:
            self.errors.append(
                Error(identifier='form.field.password',
                      title='Password and verification mismatch'))
            self.errors.append(
                Error(identifier='form.field.verif',
                      title='Password and verification mismatch'))
            self.flash(_(u'Password and verification mismatch.'))
            return FAILURE

        existing = session.query(Account).get(data['email'])
        if existing is not None:
            self.flash(_(u'User with given email already exists.'))
            self.errors.append(
                Error(identifier='form.field.email',
                      title='Email already exists'))
            return FAILURE

        # pop the captcha and verif, it's not a needed data
        data.pop('verif')
        data.pop('captcha')


        # create it
        account = Account(**data)
        code = account.activation = str(uuid.uuid1())
        session.add(account)
        session.flush()
        session.refresh(account)

        base_url = self.application_url().replace('/register', '')
        # send email
        send_activation_code(data['name'], data['email'], code, base_url)
        # redirect
        self.flash(_(u'Account added with success.'))
        self.redirect('%s/registered' % self.application_url())
        return SUCCESS


@menuentry(IDocumentActions, order=20)
class DeletedAccount(DeleteForm):
    context(Account)
    name('delete')
    require('manage.company')
    title(_(u'Delete'))

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS


@menuentry(IDocumentActions, order=10)
class TransfertCompany(Form):
    name('transfer.company')
    context(Company)
    layer(ICompanyRequest)
    title(_(u'Transfer the company'))
    require('manage.company')

    dataValidators = []
    fields = Fields(ICompanyTransfer)

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()

        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        # create it
        account = data['account']
        self.context.account_id = account

        # redirect
        self.flash(_(u'Company transfered with success.'))
        self.redirect(self.application_url())
        return SUCCESS


#@menuentry(IPersonalMenu, order=10)
class TranserCompany(uvclight.MenuItem):
    context(Interface)
    layer(ICompanyRequest)
    title(_(u'Transfer the company'))
    require('manage.company')
    uvclight.menu(IPersonalMenu)

    @property
    def action(self):
        return self.view.application_url() + '/transfer/company'


class GlobalTransfertCompany(Form):
    name('transfer.company')
    context(Interface)
    layer(ICompanyRequest)
    title(_(u'Transfer the company'))
    require('manage.company')

    dataValidators = []
    fields = Fields(ICompanies, ICompanyTransfer)

    @property
    def action_url(self):
        return self.request.path

    #def action(self):
    #    return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()

        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        # create it
        company = data['company']
        account = data['account']
        company.account_id = account

        # redirect
        self.flash(_(u'Company transfered with success.'))
        self.redirect(self.application_url())
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class CreateCompany(Form):
    name('add.company')
    context(Account)
    layer(ICompanyRequest)
    title(_(u'Add a company'))
    require('manage.company')

    dataValidators = []
    fields = Fields(ICompany).select('name', 'mnr')

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        session = get_session('school')

        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        # create it
        company = Company(**data)
        company.account_id = self.context.email
        session.add(company)
        session.flush()
        session.refresh(company)

        # redirect
        base_url = self.url(self.context)
        self.flash(_(u'Company added with success.'))
        self.redirect(base_url)
        return SUCCESS


@menuentry(IDocumentActions, order=20)
class DeletedCompany(DeleteForm):
    context(Company)
    name('delete')
    require('manage.company')
    title(_(u'Delete'))

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class CreateCourse(Form):
    context(Company)
    name('add.course')
    require('manage.company')
    title(_(u'Add a course'))

    fields = Fields(ICourse).select(
        'name', 'criterias',
        'quizz_type') + Fields(IClassSession).select('startdate', 'duration', 'about')

    def update(self):
        all_dates.need()
        datepicker_de.need()
        wysiwyg.need()
        Form.update(self)

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
        csdata = dict(
            startdate=data.pop('startdate'),
            duration=data.pop('duration'),
            about=data.pop('about')
        )
        course = Course(**data)
        course.company_id = self.context.id
        session.add(course)
        session.flush()
        session.refresh(course)
        clssession = ClassSession(**csdata)

        clssession.course_id = course.id
        clssession.company_id = self.context.id
        session.add(clssession)
        session.flush()
        session.refresh(clssession)
        self.flash(_(u'Course added with success.'))
        self.redirect('%s/%s' % (self.url(self.context), course.id))
        return SUCCESS


class CourseSession(Adapter):
    context(IClassSession)
    provides(ICourseSession)

    @apply
    def name():
        def fget(self):
            return self.context.name
        def fset(self, value):
            self.context.name = value
        return property(fget, fset)

    @apply
    def criterias():
        def fget(self):
            return self.context.criterias
        def fset(self, value):
            self.context.criterias = value
        return property(fget, fset)

    @apply
    def quizz_type():
        def fget(self):
            return self.context.quizz_type
        def fset(self, value):
            self.context.quizz_type = value
        return property(fget, fset)

    @apply
    def startdate():
        def fget(self):
            return self.context.course.startdate
        def fset(self, value):
            self.context.course.startdate = value
        return property(fget, fset)

    @apply
    def duration():
        def fget(self):
            return self.context.course.duration
        def fset(self, value):
            self.context.course.duration = value
        return property(fget, fset)

    @apply
    def about():
        def fget(self):
            return self.context.course.about
        def fset(self, value):
            self.context.course.about = value
        return property(fget, fset)


@menuentry(IDocumentActions, order=10)
class EditCourse(EditForm):
    context(IClassSession)
    name('edit_course')
    require('manage.company')
    title(_(u'Edit the course'))

    dataManager = makeAdaptiveDataManager(ICourseSession)
    fields = Fields(ICourseSession).select(
        'name', 'criterias', 'quizz_type', 'startdate', 'duration', 'about')

    def update(self):
        all_dates.need()
        datepicker_de.need()
        wysiwyg.need()
        Form.update(self)
    
    @property
    def action_url(self):
        return self.request.path


@menuentry(IDocumentActions, order=10)
class EditCourseBase(EditForm):
    context(Course)
    name('edit')
    require('manage.company')
    title(_(u'Edit the course'))

    fields = Fields(ICourse).select(
        'name', 'startdate')

    @property
    def action_url(self):
        return self.request.path

@menuentry(IDocumentActions, order=20)
class DeleteCourse(DeleteForm):
    context(Course)
    name('delete')
    require('manage.company')
    title(_(u'Delete'))

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class PopulateCourse(Form):
    context(IClassSession)
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
    template = get_template('wizard2.pt', __file__)

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
            values = SimpleVocabulary([
                    SimpleTerm(value=c.strip(), token=idx, title=c.strip())
                    for idx, c in enumerate(criteria.items.split('\n'), 1)
                    if c.strip()])

            criteria_field = Choice(
                __name__ = 'criteria_%s' % criteria.id,
                title=criteria.title,
                vocabulary=values,
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
        quizz.session_id = self.context.session_id

        session.add(self.context)
        session.add(quizz)
        self.flash(_(u'Thank you for answering the quizz'))
        self.redirect(self.request.url)
        return SUCCESS


def company_criterias(context):
    for criteria in context.criterias:
        vocabulary = SimpleVocabulary(
            [SimpleTerm(value=i.strip(), title=i.strip(), token=idx)
             for idx, i in enumerate(criteria.items.split('\n'), 1)
             if i.strip()])
        yield Set(
            __name__= '%i' % criteria.id,
            title=criteria.title,
            value_type=Choice(vocabulary=vocabulary),
            required=False)


class CriteriaFiltering(Form):
    baseclass()

    ignoreContent = True
    dataValidators = []
    criterias = {}

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


@menuentry(IContextualActionsMenu, order=10)
class ClassStats(CriteriaFiltering):
    context(ClassSession)
    name('session.stats')
    title(_(u'Statistics'))
    require('manage.company')
    layer(ICompanyRequest)

    @property
    def fields(self):
        return Fields(*list(company_criterias(self.context.course)))


@menuentry(IContextualActionsMenu, order=10)
class CourseStats(CriteriaFiltering):
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


@menuentry(IContextualActionsMenu, order=10)
class CourseDiff(CriteriaFiltering):
    context(Course)
    name('course.diff')
    title(_(u'Diff'))
    require('manage.company')
    layer(ICompanyRequest)

    @property
    def fields(self):
        return Fields(*list(company_criterias(self.context)))
