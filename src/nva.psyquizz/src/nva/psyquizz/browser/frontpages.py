# -*- coding: utf-8 -*-

from ..apps import anonymous, admin
from ..i18n import _
from ..interfaces import ICompanyRequest, IManagingRequest
from ..models import Company, Student, Course
from ..models import IQuizz
from cromlech.browser import exceptions
from dolmen.menu import menuentry, order
from uvc.design.canvas import IContextualActionsMenu
from uvclight import Page
from uvclight import layer, name, context, title, get_template
from uvclight.auth import require


@menuentry(IContextualActionsMenu, order=0)
class SchoolHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(admin.School)
    layer(IManagingRequest)
    require('manage.school')
    order(0)

    template = get_template('school.pt', __file__)


@menuentry(IContextualActionsMenu, order=0)
class SchoolCompanyHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Company)
    layer(IManagingRequest)
    require('manage.school')
    
    template = get_template('company.pt', __file__)


@menuentry(IContextualActionsMenu, order=0)
class SchoolCourseHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Course)
    layer(IManagingRequest)
    require('manage.school')

    template = get_template('course.pt', __file__)


@menuentry(IContextualActionsMenu, order=0)
class CompanyHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Company)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('company.pt', __file__)


@menuentry(IContextualActionsMenu, order=0)
class CompanyCourseHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Course)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('course.pt', __file__)


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
