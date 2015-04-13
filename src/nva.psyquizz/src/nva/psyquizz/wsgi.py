# -*- coding: utf-8 -*-

from . import Base
from .apps import admin, company, anonymous, remote
from cromlech.configuration.utils import load_zcml
from cromlech.i18n import register_allowed_languages
from cromlech.sqlalchemy import create_and_register_engine
from paste.urlmap import URLMap
from ul.auth import GenericSecurityPolicy
from zope.i18n import config
from zope.security.management import setSecurityPolicy


def routing(conf, files, session_key, **kwargs):
    global ALLOWED_LANGUAGES
    
    languages = kwargs['langs']
    allowed = languages.strip().replace(',', ' ').split()
    register_allowed_languages(allowed)
    config.ALLOWED_LANGUAGES = None

    load_zcml(kwargs['zcml'])


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
    root['/json'] = remote.Application(session_key, engine, name)

    return root
