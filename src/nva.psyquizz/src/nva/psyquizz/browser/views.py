# -*- coding: utf-8 -*-

import json

from collections import OrderedDict
from ..apps import anonymous
from ..i18n import _
from ..interfaces import ICompanyRequest, IRegistrationRequest
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
from zope import interface
from uvc.design.canvas import IPersonalMenu


class LogoutMenu(MenuItem):
   context(interface.Interface)
   menu(IPersonalMenu)
   title(u'Logout')
   layer(ICompanyRequest)

   @property
   def action(self):
       return self.view.application_url() + '/logout'


class Logout(View):
   context(interface.Interface)

   def update(self):
       session = getSession()
       if session:
           del session['username']

   def render(self):
       return self.redirect(self.application_url())


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

    @property
    def url(self):
        return self.view.url(self.context) + '/criterias'


class Registered(Page):
    name('registered')
    layer(IRegistrationRequest)
    require('zope.Public')

    def render(self):
        return u"Ihre Registrierung war erfolgreich. Sie erhalten in Kürze eine E-Mail mit den Aktivierungslink"


