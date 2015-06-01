# -*- coding: utf-8 -*-

SESSION_NAME = ''


import uvclight
from cromlech.browser import IPublicationRoot
from cromlech.sqlalchemy import get_session
from sqlalchemy import String, Integer, Column
from sqlalchemy.ext.declarative import declarative_base
from uvclight.backends.sql import SQLPublication
from ul.auth import SecurePublication
from ul.browser.decorators import with_zcml, with_i18n
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import implementer
from zope.location import Location, ILocation
from dolmen.sqlcontainer import SQLContainer
from fanstatic import Library, Resource


library = Library('nva.psyquizz', 'static')

#chartjs = Resource(library, 'Chart.js')
#charthbar = Resource(library, 'Chart.StackedBar.js', depends=[chartjs])

charthjs = Resource(library, 'ChartNew.js')
quizzjs = Resource(library, 'quizz.js', depends=[charthjs, ])

Base = declarative_base()
