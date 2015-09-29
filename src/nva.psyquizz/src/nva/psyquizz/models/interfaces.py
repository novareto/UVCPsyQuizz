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


ABOUT_TEXT = u"""
Liebe Kolleginnen und Kollegen, <br>
<p> herzlich Willkommen zu unserer Befragung „Gemeinsam zu gesunden Arbeitsbedingungen“! </p>
<p>Der Fragebogen besteht aus insgesamt 26 Fragen; das Ausfüllen wird ca. 5 Minuten dauern.</br>
Bitte beantwortet Sie alle Fragen des Fragebogens. Beim Beantworten der Fragen kann es hilfreich sein,
nicht zu lange über die einzelnen Fragen nachzudenken. Meist ist der erste Eindruck auch der treffendste.</p> </br>
<p>Wir möchten nochmal darauf hinweisen, dass Ihre Angaben absolut vertraulich behandelt werden. </br>Ein Rückschluss auf einzelne Personen wird nicht möglich sein.</p>
<p>Sollten Sie Fragen oder Anmerkungen haben, wenden Sie sich bitte an:</p> </br>
    <span style="background-color: rgb(255, 255, 0);"> Ansprechpartner und Kontaktdaten </span> </br>
    Wir freuen uns auf Ihre Rückmeldungen!
"""



def deferred(name):
    @provider(IContextSourceBinder)
    def vocabulary(context):
        return deferred_vocabularies[name](context)
    return vocabulary


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
        clean = filter(None, items.split('\n'))
        if len(clean) < 2:
            raise Invalid(_(u"Please provide at least 2 criteria items."))


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
        description=u"Bitte tragen Sie hier die achtstellige Mitgliedsnummer Ihres Unternehmens bei der BG ETEM ein.",
        required=True,
    )

    courses = schema.Set(
        title=_(u"Courses"),
        required=False,
    )


class IClassSession(ILocation, IContent):

    startdate = schema.Date(
        title=_(u"Start date"),
        required=True,
        )

    duration = schema.Choice(
        title=_(u"Duration of the session's validity"),
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
        required=True,
        )

    quizz_type = schema.Choice(
        title=_(u"Quizz"),
        source=deferred('quizz_choice'),
        required=True,
        )

    criterias = schema.Set(
        title=_(u"Criterias"),
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
