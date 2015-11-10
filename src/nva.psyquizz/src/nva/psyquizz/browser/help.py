# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from zope.interface import Interface
from uvc.design.canvas import IAboveContent


class HelpPage(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IAboveContent)
    template = uvclight.get_template('helppage.cpt', __file__)
