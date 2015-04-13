# -*- coding: utf-8 -*-

import uuid

from . import TrueOrFalse, IQuizz
from .. import Base

from cromlech.sqlalchemy import get_session
from datetime import datetime
from grokcore.component import global_utility
from sqlalchemy import *
from sqlalchemy.orm import aliased
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from uvc.content.interfaces import IContent
from uvclight.directives import traversable
from zope import schema
from zope.interface import Interface, implementer
from zope.location import ILocation, Location, LocationProxy
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class IGroup1(Interface):

    question1 = schema.Choice(
        title=u"1.1",
        description=u"Is Godzilla a lizard ?",
        vocabulary=TrueOrFalse,
        required=True,
        )


class IGroup2(Interface):

    question2 = schema.Choice(
        title=u"2.1",
        description=u"Is Zorro a spanish animal ?",
        vocabulary=TrueOrFalse,
        required=True,
        )


class IGroup3(Interface):

    question3 = schema.Choice(
        title=u"3.1",
        description=u"Are you a robot ?",
        vocabulary=TrueOrFalse,
        required=True,
        )


IGroup1.setTaggedValue('label', 'Questions 1')
IGroup2.setTaggedValue('label', 'Questions 2')
IGroup3.setTaggedValue('label', 'Questions 3')


class IQuizz2(IQuizz, IGroup1, IGroup2, IGroup3):
    pass


@implementer(IQuizz2)
class Quizz2(Base, Location):

    __tablename__ = 'quizz2'
    __schema__ = IQuizz2
    __title__ = u"Some other Quizz"

    id = Column('id', Integer, primary_key=True)

    # Link
    student_id = Column(String, ForeignKey('students.access'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    company_id = Column(String, ForeignKey('companies.name'))

    # Quizz
    completion_date = Column('completion_date', DateTime)
    question1 = Column('question1', Boolean)
    question2 = Column('question2', Boolean)
    question3 = Column('question3', Boolean)
    extra_questions = Column('extra_questions', Text)


global_utility(Quizz2, provides=IQuizz, name='quizz2', direct=True)
