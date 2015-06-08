# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from uvclight.directives import traversable
from zope.interface import Interface, implementer
from zope.location import Location
from . import IntIds
from .criterias import criterias_table
from .interfaces import ICourse


@implementer(ICourse)
class Course(Base, Location):
    traversable('criterias', 'students', 'sessions')

    isEditable = True
    isDeletable = True
    
    __tablename__ = 'courses'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    startdate = Column('startdate', Date)
    company_id = Column(String, ForeignKey('companies.name'))
    quizz_type = Column('quizz_type', String)
    extra_questions = Column('extra_questions', Text)

    students = relationship(
        "Student", backref="course",
        collection_class=set)

    _sessions = relationship(
        "ClassSession", backref=backref("course", uselist=False),
        collection_class=IntIds)
    
    criterias = relationship(
        "Criteria", secondary=criterias_table, backref="courses",
        collection_class=set)

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)

    @property
    def __name__(self):
        return str(self.id)

    @property
    def sessions(self):
        self._sessions.__name__ = 'sessions'
        self._sessions.__parent__ = self
        # directlyProvides(self._sessions, ISessions)
        return self._sessions
    
    @property
    def uncomplete(self):
        for key, student in self._students.items():
            student.__parent__ = self
            if student.completion_date is None:
                yield student

    @property
    def complete(self):
        for key, student in self._students.items():
            student.__parent__ = self
            if student.completion_date is not None:
                yield student
