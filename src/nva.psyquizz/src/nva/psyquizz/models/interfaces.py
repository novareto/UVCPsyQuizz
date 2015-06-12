# -*- coding: utf-8 -*-

from nva.psyquizz.i18n import _
from uvc.content.interfaces import IContent
from zope import schema
from zope.interface import Interface
from zope.location import ILocation
from . import deferred_vocabularies, vocabularies
from grokcore.component import provider
from zope.schema.interfaces import IContextSourceBinder


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


class IAccount(ILocation, IContent):

    name = schema.TextLine(
        title=_(u"Fullname"),
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


class IStudent(ILocation, IContent):

    access = schema.TextLine(
        title=u"Access string",
        required=True,
    )

    email = schema.TextLine(
        title=u"Email",
        required=True,
    )
