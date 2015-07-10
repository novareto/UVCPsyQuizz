import uvclight 
from uvc.entities.browser.managers import IBelowContent


class Wizard(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.name('wizard')

    template = uvclight.get_template('wizard_company.cpt', __file__)
