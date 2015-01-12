# -*- coding: utf-8 -*-

from cromlech.browser import ITypedRequest
from cromlech.sqlalchemy import get_session
from zope.interface import Interface, invariant, Invalid
from zope.schema import TextLine


ERROR_MESSAGE_TYPE = u'error'


class IBatch(Interface):
    pass


class ISheet(Interface):
    pass


class IHome(Interface):
    pass


class ITreeHome(Interface):
    pass


class IVerifRequest(ITypedRequest):
    pass
