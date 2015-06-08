# -*- coding: utf-8 -*-

import uuid

from nva.psyquizz import Base
from nva.psyquizz.models.interfaces import IQuizz, IStudent
from datetime import datetime
from sqlalchemy import *
from zope.interface import implementer
from zope.location import Location


@implementer(IQuizz, IStudent)
class Student(Base, Location):

    isEditable = True
    isDeletable = True
    
    __tablename__ = 'students'

    access = Column('access', String, primary_key=True)
    email = Column('email', String)

    # Relationships
    course_id = Column(Integer, ForeignKey('courses.id'))
    company_id = Column(String, ForeignKey('companies.name'))
    session_id = Column(String, ForeignKey('sessions.id'))

    # Quizz
    quizz_type = Column('quizz_type', String)
    completion_date = Column('completion_date', DateTime)

    @staticmethod
    def generate_access():
        return unicode(uuid.uuid4())

    def complete_quizz(self):
        self.completion_date = datetime.now()

    @property
    def __name__(self):
        return self.access

    @__name__.setter
    def __name__(self, value):
        pass
