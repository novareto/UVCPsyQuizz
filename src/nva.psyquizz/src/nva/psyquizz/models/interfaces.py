# -*- coding: utf-8 -*-

import datetime
from . import deferred_vocabularies, vocabularies
from grokcore.component import provider
from nva.psyquizz.i18n import _
from uvc.content.interfaces import IContent
from zope import schema
from zope.interface import invariant, Invalid, Interface
from zope.location import ILocation
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


ABOUT_TEXT = u"""
Liebe Kolleginnen und Kollegen, <br>
<p> herzlich Willkommen zu unserer Befragung „Gemeinsam zu gesunden Arbeitsbedingungen“! </p>

<p>Der Fragebogen umfasst 26 Fragen. Bitte beantworteten Sie alle Fragen des Fragebogens.
Beim Beantworten der Fragen kann es hilfreich sein, nicht zu lange über die einzelnen Fragen
nachzudenken. Meist ist der erste Eindruck auch der treffendste.“</p> </br>
<p>Wir möchten nochmal darauf hinweisen, dass Ihre Angaben absolut vertraulich behandelt werden. </br>Ein Rückschluss auf einzelne Personen wird nicht möglich sein.</p>
<p>Sollten Sie Fragen oder Anmerkungen haben, wenden Sie sich bitte an:</p> </br>
    <span> A n s p r e c h p a r t n e r   u n d    K o n t a k t d a t e n </span> </br>
    Wir freuen uns auf Ihre Rückmeldungen!
"""

ABOUT_TEXT = u"""
<blockquote>
<p>
Sie können das folgenden Musteranschreiben nutzen, um Ihre Beschäftigten über die 
Befragung zu informieren und den Link zum „Fragebogen“ zu verteilen.  
Fügen Sie den Text dazu in eine E-Mail ein, passen ihn nach Ihren Vorstellungen an und 
versenden ihn an Ihre Beschäftigten.
</p>
</blockquote>


<p>Liebe Kolleginnen und Kollegen,</p>
<p> herzlich Willkommen zu unserer Befragung „Gemeinsam zu gesunden Arbeitsbedingungen“! </p>
<p>Der Fragebogen besteht aus insgesamt 26 Fragen; das Ausfüllen wird ca. 5 Minuten dauern. Bitte beantworteten Sie alle Fragen des Fragebogens. Beim Beantworten der Fragen kann es hilfreich sein, nicht zu lange über die einzelnen Fragen nachzudenken. Meist ist der erste Eindruck auch der treffendste.</p>
<p>Wir möchten nochmal darauf hinweisen, dass Ihre Angaben absolut vertraulich behandelt werden. Ein Rückschluss auf einzelne Personen wird nicht möglich sein.</p>
<p>Sollten Sie Fragen oder Anmerkungen haben, wenden Sie sich bitte an:</p>
<p> <span style="background-color: rgb(255, 255, 0);">Ansprechpartner und Kontaktdaten </span></p>
<p>Wir freuen uns auf Ihre Rückmeldungen!</p>
"""



def deferred(name):
    @provider(IContextSourceBinder)
    def vocabulary(context):
        return deferred_vocabularies[name](context)
    return vocabulary


@provider(IContextSourceBinder)
def vocab_type(context):
    rc = [SimpleTerm('1', '1', u'Energieversorgungsunternehmen'),
          SimpleTerm('2', '2', u'Betriebe der Gas-, Fernwärme- und Wasserversorgung sowie Abwasserentsorgung'),
          SimpleTerm('3', '3', u'Betriebe für elektrotechnische, feinmechanische und augenoptische Erzeugnisse'),
          SimpleTerm('4', '4', u'Mess-, Informations- und Medizintechnik'),
          SimpleTerm('5', '5', u'Luft- und Raumfahrzeugtechnik'),
          SimpleTerm('6', '6', u'Elektroinstallationsbetriebe'),
          SimpleTerm('7', '7', u'Graveure, Goldschmiede, Uhrmacher'),
          SimpleTerm('8', '8', u'Herstellung und Bearbeitung von Textilien, Bekleidung, Wäsche'),
          SimpleTerm('9', '9', u'Herstellung von Schuhen'),
          SimpleTerm('10', '10', u'Offset-, Sieb-, Tief- und Digitaldruck'),
          SimpleTerm('11', '11', u'Grafik und Druckvorstufe'),
          SimpleTerm('12', '12', u'Herstellung von Wellpappe, Kartonagen'),
          SimpleTerm('13', '13', u'Papierverarbeitung'),
          SimpleTerm('14', '14', u'Fotografie und Bildjournalismus'),
          SimpleTerm('15', '15', u'sonstige'),
          ]
    return SimpleVocabulary(rc)


@provider(IContextSourceBinder)
def vocab_employees(context):
    rc = [SimpleTerm('1', '1', u'Weniger als 10'),
          SimpleTerm('2', '2', u'Mehr als 10 und weniger als 50'),
          SimpleTerm('3', '3', u'Mehr als 50 und weniger als 250'),
          SimpleTerm('4', '4', u'Mehr als 250 und weniger als 500'),
          SimpleTerm('5', '5', u'Mehr als 500')
          ]
    return SimpleVocabulary(rc)


class IQuizz(Interface):
    pass


class ICriterias(IContent):
    pass


class ICriteria(IContent):

    title = schema.TextLine(
        title=_(u"Label"),
        description=_(u"Description Label"),
        required=True,
    )

    items = schema.Text(
        title=_(u"Please enter one criteria per line"),
        description=_(u"Description items"),
        required=True,
    )

    @invariant
    def check_items(data):
        items = data.items
        msg = _('Bitte geben Sie mindestens 2 Kriterien in der Auswertungsgruppe an')
        if not items:
            raise Invalid(msg)
        clean = filter(None, items.split('\n'))
        if len(clean) < 2:
            raise Invalid(msg)


class IAccount(ILocation, IContent):

    name = schema.TextLine(
        title=_(u"Fullname"),
        description=_(u"Please give your Fullname here"),
        required=True,
    )

    email = schema.TextLine(
        title=_(u"E-Mail"),
        description=u"Ihre E-Mailadresse benötigen Sie später beim Login.",
        required=True,
    )

    password = schema.Password(
        title=_(u"Password for observation access"),
        description=u"Bitte vergeben Sie ein Passwort (mindestens acht Zeichen).",
        required=True,
    )

    activated = schema.Datetime(
        title=_(u"Active account since"),
        required=False,
    )


class ICompanyTransfer(Interface):

    account_id = schema.Choice(
        title=_(u"Accounts"),
        source=deferred('accounts_choice'),
        required=True,
        )


class ICompanies(Interface):

    company = schema.Choice(
        title=_(u"Company"),
        source=deferred('companies_choice'),
        required=True,
        )


class ICompany(ILocation, IContent):

    name = schema.TextLine(
        title=_(u"Company name"),
        required=True,
    )

    mnr = schema.TextLine(
        title=_(u"Company ID"),
        description=u"Bitte geben Sie hier die ersten acht Stellen Ihrer Mitgliedsnummer bei der BG ETEM ein.",
        required=True,
    )

    courses = schema.Set(
        title=_(u"Courses"),
        required=False,
    )

    exp_db = schema.Bool(
        title=_(u'Forschungsdatenbank'),
        description=_(u'Dürfen wir die Ergebnisse in der ForschungsDB verwenden'),
        required=True,
    )

    employees = schema.Choice(
        title=_(u'Employees'),
        description=_(u'Employees_desc'),
        required=False,
        source=vocab_employees,
    )

    type = schema.Choice(
        title=_(u'Type'),
        description=_(u'Type_desc'),
        required=False,
        source=vocab_type,
    )


class IClassSession(ILocation, IContent):

    startdate = schema.Date(
        title=_(u"Start date"),
        description=u"Bitte geben Sie an, ab wann die Befragungsseite für Ihre Beschäftigten zugänglich sein soll.",
        required=True,
        )

    duration = schema.Choice(
        title=_(u"Duration of the session's validity"),
        description=u"Bitte geben Sie an, wie lange die Befragungsseite für Ihre Beschäftigten zugänglich sein soll.",
        required=True,
        vocabulary=vocabularies.durations,
        )

    students = schema.Set(
        title=_(u"Students"),
        required=False,
        )

    about = schema.Text(
        title=_(u"About"),
        description=_("This Text gives Information about the Course to Participants"),
        required=False,
        default=ABOUT_TEXT,
        )

    @invariant
    def check_date(data):
        date = data.startdate
        if date is not None and date < datetime.date.today():
            raise Invalid(_(u"You can't set a date in the past."))


class ICourse(ILocation, IContent):

    name = schema.TextLine(
        title=_(u"Course name"),
        description=u"Bitte geben Sie Ihrer Befragung eine eindeutige Bezeichnung wie z.B. Beurteilung Psychischer Belastung – Gesamtbetrieb",
        required=True,
        )

    quizz_type = schema.Choice(
        title=_(u"Quizz"),
        source=deferred('quizz_choice'),
        required=True,
        )

    criterias = schema.Set(
        title=_(u"Auswertungsgruppen festlegen"),
        description=u"Bitte entfernen Sie das Häkchen, falls Sie einzelne Auswertungsgruppen nicht in Ihrer Befragung verwenden wollen.",
        value_type=schema.Choice(source=deferred('criterias_choice')),
        required=False,
        )

    extra_questions = schema.Text(
        title=_(u"Complementary questions for the course"),
        description=_(u"Type your questions : one per line."),
        required=False,
        )


class ICourseSession(IClassSession, ICourse):
    pass


class IStudent(ILocation, IContent):

    access = schema.TextLine(
        title=u"Access string",
        required=True,
    )

    email = schema.TextLine(
        title=u"Email",
        required=True,
    )
