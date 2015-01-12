# -*- coding: utf-8 -*-

import uuid

from .. import Base
from crate.client.sqlalchemy.types import Object, ObjectArray
from sqlalchemy import *
from sqlalchemy.orm import relationship
from zope.interface import Interface, implementer
from zope.schema import TextLine, Set
from zope.location import ILocation
from dolmen.sqlcontainer import SQLContainer
from uvc.content.interfaces import IContent


class ICompany(IContent):

    name = TextLine(
        title=u"Company name",
        required=True,
        )
    
    students = Set(
        title=u"Students",
        required=False,
        )


class IStudent(IContent):

    access = TextLine(
        title=u"Access string",
        required=True,
        )

    email = TextLine(
        title=u"Email",
        required=True,
        )


@implementer(IStudent)
class Student(Base):

    __tablename__ = 'students'

    access = Column('access', String, primary_key=True)
    email = Column('email', String)
    company_id = Column(Integer, ForeignKey('companies.name'))

    @staticmethod
    def generate_access():
        return unicode(uuid.uuid4())


@implementer(ICompany)
class Company(Base):

    __tablename__ = 'companies'
    model = Student

    name = Column('name', String, primary_key=True)
    password = Column('password', String)
    students = relationship("Student", backref="company")

    @property
    def id(self):
        return self.name
    
    @classmethod
    def generate_students(cls, nb):
        for i in xrange(0, nb):
            access = cls.model.generate_access()
            yield cls.model(access=access)


