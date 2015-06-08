# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import uvclight
from zope.interface import Interface
from grokcore.component import adapts
from dolmen.forms.ztk.widgets import choice
from uvc.themes.btwidgets.widgets.choice import RadioFieldWidget
from nva.psyquizz.interfaces import IQuizzLayer


class RadioFieldWidget(RadioFieldWidget):
    adapts(choice.ChoiceField, Interface, IQuizzLayer)
    template = uvclight.get_template('radiofieldwidget.cpt', __file__)
