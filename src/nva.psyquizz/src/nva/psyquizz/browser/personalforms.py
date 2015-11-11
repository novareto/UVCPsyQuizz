# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from zope.interface import Interface
from uvc.design.canvas import IDocumentActions, IPersonalMenu
from uvclight import Form, EditForm, name, context, layer, title, menuentry
from uvclight import Fields, action, SUCCESS, FAILURE
from uvclight.auth import require
from ..models import IAccount, Account, Company, ICompanyTransfer, ICompanies
from ..interfaces import ICompanyRequest
from ..i18n import _
from dolmen.forms.base.utils import apply_data_event
from uvc.composedview.components import ComposedPage, ITab


class MyPrefs(ComposedPage):
    uvclight.context(Account)
    uvclight.name('myprefs')
    uvclight.auth.require('manage.company')


@menuentry(IDocumentActions, order=20)
class EditAccount(EditForm):
    uvclight.provides(ITab)
    context(MyPrefs)
    name('edit')
    require('manage.company')
    title(_(u'Edit Account'))

    def __init__(self, context, request):
        super(EditAccount, self).__init__(context, request)
        self.setContentData(context.context)

    label = ""

    fields = Fields(IAccount).select('name', 'email', 'password')

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Update'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u"An error occured"))
            return FAILURE

        apply_data_event(self.fields, self.getContentData(), data)
        self.flash(_(u"Content updated"))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.url(self.context))
        return SUCCESS


@menuentry(IDocumentActions, order=10)
class TransfertCompany(Form):
    name('transfer.company')
    uvclight.provides(ITab)
    context(MyPrefs)
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

        account = data['account']
        self.context.account_id = account

        self.flash(_(u'Company transfered with success.'))
        self.redirect(self.application_url())
        return SUCCESS


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
    uvclight.provides(ITab)
    context(MyPrefs)
    name('transfer.company')
    layer(ICompanyRequest)
    title(_(u'Transfer the company'))
    require('manage.company')
    uvclight.baseclass()

    dataValidators = []
    fields = Fields(ICompanies, ICompanyTransfer)

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()

        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        company = data['company']
        account = data['account']
        company.account_id = account

        self.flash(_(u'Company transfered with success.'))
        self.redirect(self.application_url())
        return SUCCESS


