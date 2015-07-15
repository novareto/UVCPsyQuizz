# -*- coding: utf-8 -*-

import uvclight 
from uvc.entities.browser.managers import IBelowContent
from ..models import IAccount, ICompany, ICourse, ICriterias, IClassSession
from .. import quizzcss


class WizardViewlet(uvclight.Viewlet):
    uvclight.baseclass()
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    
    def update(self):
        quizzcss.need()


class WizardAccount(WizardViewlet):
    uvclight.context(IAccount)
    template = uvclight.get_template('wizard_account.cpt', __file__)


class WizardCompany(WizardViewlet):
    uvclight.context(ICompany)
    template = uvclight.get_template('wizard_company.cpt', __file__)


class WizardCourse(WizardViewlet):
    uvclight.context(ICourse)
    template = uvclight.get_template('wizard_course.cpt', __file__)


class WizardCriterias(WizardViewlet):
    uvclight.context(ICriterias)
    template = uvclight.get_template('wizard_criterias.cpt', __file__)


class WizardSession(WizardViewlet):
    uvclight.context(IClassSession)
    template = uvclight.get_template('wizard_session.cpt', __file__)
