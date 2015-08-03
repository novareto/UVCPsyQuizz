# -*- coding: utf-8 -*-


from ..i18n import _
from uvclight import Page
from uvclight import layer, name, context, title, get_template
from ..interfaces import ICompanyRequest
from ..models import Account
from uvclight.auth import require
from ..models.deferred import quizz_choice
from cromlech.browser import ITemplate
from uvc.entities.browser.menus import IContextualActionsMenu
from grokcore.component import adapter, implementer



class AccountHomepage(Page):
    name('ckh')
    title(_(u'Frontpage'))
    context(Account)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('ckh.pt', __file__)

    def quizz_name(self, course):
        voc = quizz_choice(course)
        return voc.getTermByToken(course.quizz_type).title


