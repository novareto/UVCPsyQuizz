# -*- coding: utf-8 -*-

import json

from collections import OrderedDict
from ..apps import anonymous
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..interfaces import QuizzAlreadyCompleted, QuizzClosed
from ..models import IQuizz, Company, Course, Student, TrueOrFalse
from dolmen.menu import menuentry
from uvc.design.canvas import IContextualActionsMenu

from uvclight import Page, View, MenuItem
from uvclight import layer, title, name, menu, context, get_template
from uvclight.auth import require
from zope.component import getUtilitiesFor, getUtility
from zope.schema import getFieldsInOrder
from cromlech.sqlalchemy import get_session
from nva.psyquizz import quizzjs


class QuizzErrorPage(Page):
    name('')
    context(QuizzAlreadyCompleted)
    require('zope.Public')

    def render(self):
        return _(u"This quizz is already completed and therefore closed.")


class CourseExpiredPage(Page):
    name('')
    context(QuizzClosed)
    require('zope.Public')

    def render(self):
        return _(u"The course access is expired.")


class CriteriasAccess(MenuItem):
    context(Company)
    name('criteria')
    title(_(u'Criterias'))
    layer(ICompanyRequest)
    menu(IContextualActionsMenu)

    url = '/criterias'
