# -*- coding: utf-8 -*-

import uvclight
from uvc.design.canvas.menus import INavigationMenu
from uvc.design.canvas import IAboveContent
from uvc.design.canvas import menus
from dolmen.message import receive
from dolmen.template import ITemplate
from grokcore.component import adapter, implementer
from ..interfaces import IQuizzLayer


class FlashMessages(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(30)
    uvclight.name('messages')

    template = uvclight.get_template('flashmessages.cpt', __file__)

    def update(self):
        received = receive()
        if received is not None:
            self.messages = list(received)
        else:
            self.messages = []


@adapter(menus.IContextualActionsMenu, IQuizzLayer)
@implementer(ITemplate)
def object_template(context, request):
    return uvclight.get_template('objectmenu.cpt', __file__)


class Home(uvclight.MenuItem):
    uvclight.title(u'Home')
    uvclight.auth.require('zope.Public')
    uvclight.menu(INavigationMenu)

    @property
    def action(self):
        return self.view.application_url()
