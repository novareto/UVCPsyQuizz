# -*- coding: utf-8 -*-

from cromlech.browser import exceptions
from uvc.themes.dguv import IDGUVRequest


class IManagingRequest(IDGUVRequest):
    pass


class ICompanyRequest(IDGUVRequest):
    pass


class IAnonymousRequest(IDGUVRequest):
    pass


class QuizzAlreadyCompleted(exceptions.HTTPForbidden):
    pass
