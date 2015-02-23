# -*- coding: utf-8 -*-

from cromlech.browser import exceptions
from uvc.themes.dguv import IDGUVRequest


class IQuizzLayer(IDGUVRequest):
    pass


class IManagingRequest(IQuizzLayer):
    pass


class ICompanyRequest(IQuizzLayer):
    pass


class IAnonymousRequest(IQuizzLayer):
    pass


class QuizzAlreadyCompleted(exceptions.HTTPForbidden):
    pass
