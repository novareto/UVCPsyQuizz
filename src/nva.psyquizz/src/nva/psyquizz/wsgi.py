# -*- coding: utf-8 -*-

from . import Base
from paste.urlmap import URLMap
from ul.auth import GenericSecurityPolicy
from ul.browser.decorators import with_zcml
from zope.security.management import setSecurityPolicy
from .apps import admin, company, anonymous
from cromlech.sqlalchemy import create_and_register_engine


@with_zcml('zcml')
def routing(conf, files, session_key, **kwargs):
    setSecurityPolicy(GenericSecurityPolicy)
    name = 'school'

    # We register our SQLengine under a given name
    dsn = "sqlite:////tmp/test.db"
    engine = create_and_register_engine(dsn, name)

    # We use a declarative base, if it exists we bind it and create
    engine.bind(Base)
    metadata = Base.metadata
    metadata.create_all(engine.engine, checkfirst=True)

    # Router
    root = URLMap()
    root['/'] = company.Application(session_key, engine, name)
    root['/admin'] = admin.Application(session_key, engine, name)
    root['/quizz'] = anonymous.Application(session_key, engine, name)

    return root
