# -*- coding: utf-8 -*-

from ..i18n import _
from ..interfaces import ICompanyRequest
from ..models import Account
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

    def quizz_name(self, course):
        voc = quizz_choice(course)
        return voc.getTermByToken(course.quizz_type).title
