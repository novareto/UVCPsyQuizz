# -*- coding: utf-8 -*-

import base64
from .. import quizzjs
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..models import Account, ClassSession
from ..models.deferred import quizz_choice
from uvclight import Page
from uvclight import layer, name, context, title, get_template
from uvclight.auth import require


class AccountHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Account)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('ckh.pt', __file__)

    def update(self):
        quizzjs.need()

    def quizz_name(self, course):
        voc = quizz_choice(course)
        return voc.getTermByToken(course.quizz_type).title

    def generic_id(self, id):
        return base64.urlsafe_b64encode(str(id + 2098) + ' complexificator')


class ExampleText(Page):
    context(ClassSession)
    layer(ICompanyRequest)
    require('manage.company')
    template = get_template('example_text.pt', __file__)

    def generic_id(self, id):
        return base64.urlsafe_b64encode(str(id + 2098) + ' complexificator')

