# -*- coding: utf-8 -*-

import uvclight
from . import Base
from .models.course import Company, Student
from cromlech.browser import IPublicationRoot
from cromlech.browser import exceptions
from cromlech.security import Principal, Interaction, unauthenticated_principal
from cromlech.sqlalchemy import get_session
from dolmen.sqlcontainer import SQLContainer
from paste.urlmap import URLMap
from sqlalchemy import String, Integer, Column
from sqlalchemy.ext.declarative import declarative_base
from ul.auth import SecurePublication, GenericSecurityPolicy
from ul.browser.decorators import with_zcml, with_i18n, sessionned
from ul.browser.publication import IBeforeTraverseEvent
from uvc.content.interfaces import IContent
from uvclight.backends.sql import SQLPublication
from uvclight.utils import current_principal
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import implementer
from zope.location import Location, ILocation
from zope.security.management import setSecurityPolicy


class Site(object):

    def __init__(self, root):
        self.root = root

    def __enter__(self):
        setSite(self.root)
        return self.root

    def __exit__(self, exc_type, exc_value, traceback):
        setSite()


@implementer(IContent, IPublicationRoot)
class School(SQLContainer):
    model = Company
    credentials = ('managers',)
    
    def getSiteManager(self):
        return getGlobalSiteManager()


@implementer(IContent, IPublicationRoot)
class QuizzBoard(SQLContainer):
    model = Student

    def getSiteManager(self):
        return getGlobalSiteManager()


@uvclight.subscribe(Company, IBeforeTraverseEvent)
def secure(obj, event):
    principal = current_principal()
    if 'manage.school' in principal.permissions:
        pass
    elif principal.id == obj.name:
        pass
    else:
        raise exceptions.HTTPForbidden(obj)

        
class AdminPublisher(SQLPublication, SecurePublication):

    def setup_database(self, engine):
        pass

    def principal_factory(self, username):
        principal = SecurePublication.principal_factory(self, username)
        if username == 'admin':
            principal.permissions = set(('manage.school',))
            principal.roles = set()
        return principal
    
    def site_manager(self, environ):
        return Site(School(None, '', self.name))

    @classmethod
    def create(cls, gc, name, session_key, zcml_file, dsn='sqlite:////tmp/test.db'):
        return super(AdminPublisher, cls).create(
            gc, session_key, dsn=dsn, name=name, base=Base, zcml_file=zcml_file)


class Publisher(SQLPublication):

    def setup_database(self, engine):
        pass

    def site_manager(self, environ):
        return Site(QuizzBoard(None, '', self.name))

    @classmethod
    def create(cls, gc, name, session_key, zcml_file, dsn='sqlite:////tmp/test.db'):
        return super(Publisher, cls).create(
            gc, session_key, dsn=dsn, name=name, base=Base, zcml_file=zcml_file)


    
def routing(conf, files, session_key, zcml):
    setSecurityPolicy(GenericSecurityPolicy)
    prof = AdminPublisher.create(conf, 'school', session_key, zcml_file=zcml)
    stud = Publisher.create(conf, 'school', session_key, zcml_file=zcml)
    root = URLMap()
    root['/admin'] = prof
    root['/quizz'] = stud
    return root
