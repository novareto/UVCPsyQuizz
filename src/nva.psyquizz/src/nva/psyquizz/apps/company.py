# -*- coding: utf-8 -*-

import webob.exc

from . import Site
from .. import Base
from ..models import Company
from ..interfaces import ICompanyRequest
from cromlech.browser import exceptions
from cromlech.browser import IPublicationRoot, IView, IResponseFactory
from cromlech.sqlalchemy import get_session
from cromlech.security import Interaction, unauthenticated_principal
from ul.auth import SecurePublication, ICredentials
from ul.auth.browser import Login
from ul.sql.decorators import transaction_sql
from ul.browser.decorators import sessionned
from ul.browser.context import ContextualRequest
from uvclight import GlobalUtility, name, layer
from uvclight.auth import require
from uvclight.backends.sql import SQLPublication
from zope.component import getGlobalSiteManager
from zope.location import Location
from zope.interface import alsoProvides, implementer
from zope.security.proxy import removeSecurityProxy


@implementer(ICredentials)
class CompanyAccess(GlobalUtility):
    name('company')
    
    def log_in(self, username, password, **kws):
        session = get_session('school')
        company = session.query(Company).get(username)
        if company is not None and company.password == password:
            return company
        return None


class CompanyLogin(Login):
    name('login')
    layer(ICompanyRequest)
    require('zope.Public')

    def get_credentials_managers(self):
        return (CompanyAccess(),)


@implementer(IPublicationRoot, IView, IResponseFactory)
class NoAccess(Location):

    def __init__(self, request):
        self.request = request

    def getSiteManager(self):
        return getGlobalSiteManager()

    def __call__(self):
        return CompanyLogin(self, self.request)()


class Application(SQLPublication, SecurePublication):

    layers = [ICompanyRequest,]

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
            print layers
            with ContextualRequest(environ, layers=layers) as request:
                response = self.publish_traverse(request)
                return response(environ, start_response)

        return publish(environ, start_response)
