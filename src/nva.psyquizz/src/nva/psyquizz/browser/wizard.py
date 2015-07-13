# -*- coding: utf-8 -*-

import uvclight 
from uvc.entities.browser.managers import IBelowContent
from ..models import IAccount, ICompany, ICourse, ICriterias, IClassSession


class WizardAccount(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(IAccount)

    template = uvclight.get_template('wizard_account.cpt', __file__)


class WizardCompany(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(ICompany)

    template = uvclight.get_template('wizard_company.cpt', __file__)


class WizardCourse(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(ICourse)

    template = uvclight.get_template('wizard_course.cpt', __file__)


class WizardCriterias(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(ICriterias)

    template = uvclight.get_template('wizard_criterias.cpt', __file__)


class WizardSession(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(IClassSession)

    template = uvclight.get_template('wizard_session.cpt', __file__)
