# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from zope.interface import Interface
from grokcore.component import adapts
from dolmen.forms.ztk.widgets import choice
from uvc.themes.btwidgets.widgets.choice import RadioFieldWidget
from uvc.themes.btwidgets.widgets.collection import MultiChoiceFieldWidget
from dolmen.forms.ztk.widgets.collection import SetField
from nva.psyquizz.interfaces import IQuizzLayer


class RadioFieldWidget(RadioFieldWidget):
    adapts(choice.ChoiceField, Interface, IQuizzLayer)
    template = uvclight.get_template('radiofieldwidget.cpt', __file__)


class MultiChoiceFieldWidget(MultiChoiceFieldWidget):
    adapts(SetField, choice.ChoiceField, Interface, IQuizzLayer)
    template = uvclight.get_template('multichoicefieldwidget.cpt', __file__)

    def renderableChoice(self):
        current = self.inputValue()
        base_id = self.htmlId()
        print "YES I AM IN THE GAME"
        for i, choicet in enumerate(self.choices()):
            yield {'token': choicet.token,
                   'title': choicet.title,
                   'disabled': getattr(choicet, 'disabled', None),
                   'checked': choicet.token in current,
                   'id': base_id + '-' + str(i)}
