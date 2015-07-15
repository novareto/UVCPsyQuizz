# -*- coding: utf-8 -*-

import uvclight 
from uvc.entities.browser.managers import IBelowContent
from ..models import IAccount, ICompany, ICourse, ICriterias, IClassSession
from .frontpages import CompanySessionHomepage, CriteriasListing, AccountHomepage, CompanyHomepage, CompanyCourseHomepage


class WizardAccount(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(IAccount)
    uvclight.view(AccountHomepage)

    template = uvclight.get_template('wizard_account.cpt', __file__)


class WizardCompany(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(ICompany)
    uvclight.view(CompanyHomepage)

    template = uvclight.get_template('wizard_company.cpt', __file__)


class WizardCourse(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(ICourse)
    uvclight.view(CompanyCourseHomepage)

    template = uvclight.get_template('wizard_course.cpt', __file__)


class WizardCriterias(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(ICriterias)
    uvclight.view(CriteriasListing)

    template = uvclight.get_template('wizard_criterias.cpt', __file__)


class WizardSession(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')
    uvclight.context(IClassSession)
    uvclight.view(CompanySessionHomepage)

    template = uvclight.get_template('wizard_session.cpt', __file__)
