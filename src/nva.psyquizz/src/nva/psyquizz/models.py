# -*- coding: utf-8 -*-

import uuid

from uvclight.directives import traversable
from . import Base
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import relationship
from zope.interface import Interface, implementer
from zope.schema import TextLine, Set, Choice
from zope.location import ILocation, Location
from dolmen.sqlcontainer import SQLContainer
from uvc.content.interfaces import IContent
from cromlech.sqlalchemy import get_session
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


TrueOrFalse = SimpleVocabulary([
    SimpleTerm(value=True,
               title='True'),
    SimpleTerm(value=False,
               title='False'),
    ])


class ICompany(ILocation, IContent):

    name = TextLine(
        title=u"Company name",
        required=True,
        )
    
    students = Set(
        title=u"Students",
        required=False,
        )


class IStudent(ILocation, IContent):

    access = TextLine(
        title=u"Access string",
        required=True,
        )

    email = TextLine(
        title=u"Email",
        required=True,
        )


class IQuizz(Interface):

    question1 = Choice(
        title=u"Is the sky blue ?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question2 = Choice(
        title=u"Du riechst so gut ?",
        vocabulary=TrueOrFalse,
        required=True,
        )


@implementer(IQuizz, IStudent)
class Student(Location, Base):

    __tablename__ = 'students'

    access = Column('access', String, primary_key=True)
    email = Column('email', String)
    company_id = Column(Integer, ForeignKey('companies.name'))

    # Quizz
    completion_date = Column('completion_date', DateTime)
    question1 = Column('question1', Boolean)
    question2 = Column('question2', Boolean)

    @property
    def __name__(self):
        return self.access

    @__name__.setter
    def __name__(self, value):
        pass

    @staticmethod
    def generate_access():
        return unicode(uuid.uuid4())

    def complete_quizz(self, **answers):
        self.completion_date = datetime.now()
        for key, value in answers.items():
            setattr(self, key, value)


@implementer(ICompany)
class Company(SQLContainer, Base):

    __tablename__ = 'companies'
    model = Student
    db_key = 'access'

    name = Column('name', String, primary_key=True)
    password = Column('password', String)
    students = relationship("Student", backref="company")

    @property
    def id(self):
        return self.name

    @property
    def __name__(self):
        return self.name

    @__name__.setter
    def __name__(self, value):
        pass

    @property
    def session(self):
        return get_session('school')

    @classmethod
    def generate_students(cls, nb):
        for i in xrange(0, nb):
            access = cls.model.generate_access()
            yield cls.model(access=access)

    @property
    def uncomplete(self):
        models = self.session.query(self.model).filter(
            self.model.completion_date == None)
        for model in models:
            proxy = ILocation(model)
            proxy.__parent__ = self
            yield proxy

    @property
    def complete(self):
        models = self.session.query(self.model).filter(
            self.model.completion_date != None)
        for model in models:
            proxy = ILocation(model)
            proxy.__parent__ = self
            yield proxy
