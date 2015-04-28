# -*- coding: utf-8 -*-

from . import Site
from .. import Base
from ..models import Student
from ..interfaces import IAnonymousRequest, QuizzAlreadyCompleted
from cromlech.browser import IPublicationRoot
from dolmen.sqlcontainer import SQLContainer
from uvc.content.interfaces import IContent
from uvclight.backends.sql import SQLPublication
from zope.component import getGlobalSiteManager
from zope.interface import implementer


@implementer(IContent, IPublicationRoot)
class QuizzBoard(SQLContainer):
    model = Student
    assert_key = 'completion_date'

    def getSiteManager(self):
        return getGlobalSiteManager()

    def __getitem__(self, id):
        content = SQLContainer.__getitem__(self, id)
        if getattr(content, 'completion_date') is not None:
            raise QuizzAlreadyCompleted(content)
        return content

from uvc.themes.btwidgets import IBootstrapRequest
class Application(SQLPublication):

    layers = [IBootstrapRequest, IAnonymousRequest, IBootstrapRequest]

    def setup_database(self, engine):
        pass

    def site_manager(self, environ):
        return Site(QuizzBoard(None, '', self.name))
