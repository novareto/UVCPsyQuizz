# -*- coding: utf-8 -*-

from ul.auth import ICredentials
from uvclight import GlobalUtility, name
from zope.interface import implementer
from cromlech.sqlalchemy import get_session
from .models import Company


@implementer(ICredentials)
class SchoolAccess(GlobalUtility):
    name('managers')
    
    def log_in(self, username, password, **kws):
        if username == 'admin':
            if password == 'admin':
                print 'true'
                return True
            return False
        else:
            session = get_session('school')
            account = session.query(Company).get(username)
            if account is not None and account.password == password:
                return True
        return None
