# -*- coding: utf-8 -*-

from . import Site
from ..interfaces import IManagingRequest
from ..models import Company
from uvclight import layer
from cromlech.browser import IPublicationRoot
from cromlech.security import unauthenticated_principal
from dolmen.sqlcontainer import SQLContainer
from ul.auth import ICredentials, SecurePublication
from ul.auth.browser import Login
from uvc.content.interfaces import IContent
from uvclight import GlobalUtility, name
from uvclight.backends.sql import SQLPublication
from zope.component import getGlobalSiteManager
from zope.interface import implementer


@implementer(ICredentials)
class SchoolAccess(GlobalUtility):
    name('managers')
    
    def log_in(self, username, password, **kws):
        if username == 'admin':
            if password == 'admin':
                return True
        return False


class AdminLogin(Login):
    name('login')
    layer(IManagingRequest)

    def get_credentials_managers(self):
        return (SchoolAccess(),)


@implementer(IContent, IPublicationRoot)
class School(SQLContainer):
    model = Company
    access_key = 'name'

    def getSiteManager(self):
        return getGlobalSiteManager()


class Application(SQLPublication, SecurePublication):

    layers = [IManagingRequest,]

    def setup_database(self, engine):
        pass

    def principal_factory(self, username):
        principal = SecurePublication.principal_factory(self, username)
        if principal is not unauthenticated_principal:
            principal.permissions = set(('manage.school',))
            principal.roles = set()
        return principal
    
    def site_manager(self, request):
        return Site(School(None, '', self.name))
