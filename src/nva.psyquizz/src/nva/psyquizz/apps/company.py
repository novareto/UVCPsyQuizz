# -*- coding: utf-8 -*-

import webob.exc
import urllib
import urlparse

from . import Site
from ..interfaces import ICompanyRequest
from ..models import Company
from cromlech.browser import IPublicationRoot, IView, IResponseFactory
from cromlech.browser.interfaces import ITraverser
from cromlech.security import Interaction, unauthenticated_principal
from cromlech.sqlalchemy import get_session
from datetime import datetime
from dolmen.forms.base import Fields, SuccessMarker
from ul.auth import SecurePublication, ICredentials
from ul.auth.browser import Login, ILoginForm
from ul.browser.context import ContextualRequest
from ul.browser.decorators import sessionned
from ul.sql.decorators import transaction_sql
from uvclight import GlobalUtility, name, layer, MultiAdapter, provides, adapts
from uvclight.auth import require
from uvclight.backends.sql import SQLPublication
from zope.component import getGlobalSiteManager
from zope.interface import Interface, alsoProvides, implementer
from zope.location import Location
from zope.schema import TextLine
from zope.security.proxy import removeSecurityProxy


class IActivationRequest(ICompanyRequest):
    pass
    


class ActivationTraverser(MultiAdapter):
    name('activation')
    adapts(Interface, ICompanyRequest)
    provides(ITraverser)

    def __init__(self, obj, request):
        self.obj = obj
        self.request = request
    
    def traverse(self, ns, name):
        alsoProvides(self.request, IActivationRequest)
        return self.obj


def activate_url(url, **data):
    params = data
    if 'password' in params:
        del params['password']
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(url_parts)


@implementer(ICredentials)
class CompanyAccess(GlobalUtility):
    name('company')
    
    def log_in(self, request, username, password, **kws):
        session = get_session('school')
        company = session.query(Company).get(username)
        
        if company is not None and company.password == password:
            if company.activated is not None:
                return company
            activation = kws.get('activation')
            if activation is not None:
                if activation == company.activation:
                    company.activated = datetime.now()
                    return company
                else:
                    return SuccessMarker(
                        'Activation failed', False,
                        url=activate_url(request.path, **kws))
            else:
                return SuccessMarker(
                    'Needs activation', False,
                    url=activate_url(request.path, **kws))
        return None


class IActivation(Interface):
    activation = TextLine(
        title=u'Activation code',
        required=True)
    

class CompanyLogin(Login):
    name('login')
    layer(ICompanyRequest)
    require('zope.Public')

    prefix = ''

    @property
    def action_url(self):
        return self.request.path
    
    @property
    def fields(self):
        fields = Login.fields
        if IActivationRequest.providedBy(self.request):
            fields += Fields(IActivation)
            fields['activation'].ignoreRequest = False
        for field in fields:
            field.prefix = ''
        return fields

    def credentials_managers(self):
        yield CompanyAccess()


@implementer(IPublicationRoot, IView, IResponseFactory)
class NoAccess(Location):

    def __init__(self, request):
        self.request = request

    def getSiteManager(self):
        return getGlobalSiteManager()

    def __call__(self):
        return CompanyLogin(self, self.request)()


class Application(SQLPublication, SecurePublication):

    layers = [ICompanyRequest]

    def setup_database(self, engine):
        pass

    def principal_factory(self, username):
        principal = SecurePublication.principal_factory(self, username)
        principal.permissions = set(('manage.company',))
        principal.roles = set()
        return principal

    def site_manager(self, request):
        username = request.principal.id
        if username != unauthenticated_principal.id:
            session = get_session(self.name)
            company = session.query(Company).get(username)
            if company is not None:
                company.getSiteManager = getGlobalSiteManager
                alsoProvides(company, IPublicationRoot)
                return Site(company)
        return Site(NoAccess(request))

    def publish_traverse(self, request):
        user = self.get_credentials(request.environment)
        request.principal = self.principal_factory(user)
        try:
            with self.site_manager(request) as site:
                with Interaction(request.principal):
                    response = self.publish(request, site)
                    response = removeSecurityProxy(response)
                    return response
        except webob.exc.HTTPException as e:
            return e

    def __call__(self, environ, start_response):

        @sessionned(self.session_key)
        @transaction_sql(self.engine)
        def publish(environ, start_response):
            layers = self.layers or list()
            with ContextualRequest(environ, layers=layers) as request:
                response = self.publish_traverse(request)
                return response(environ, start_response)

        return publish(environ, start_response)
