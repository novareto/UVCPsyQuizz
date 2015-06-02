# -*- coding: utf-8 -*-

import uuid

from .. import Base
from ..i18n import _
from ..sqlutils import IntIds
from cromlech.sqlalchemy import get_session
from datetime import datetime, date, timedelta
from grokcore.component import provider
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.collections import collection
from uvc.content.interfaces import IContent
from uvclight.directives import traversable
from zope import schema
from zope.component import getUtilitiesFor
from zope.interface import Interface, implementer, directlyProvides
from zope.location import ILocation, Location, LocationProxy
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class IQuizz(Interface):
    pass


TrueOrFalse = SimpleVocabulary([
    SimpleTerm(value=True,
               title='eher Ja'),
    SimpleTerm(value=False,
               title='eher Nein'),
    ])


LessToMore = SimpleVocabulary([
    SimpleTerm(value=1,
               title='sehr wening'),
    SimpleTerm(value=2,
               title='ziemlich wenig'),
    SimpleTerm(value=3,
               title='etwas'),
    SimpleTerm(value=4,
               title='ziemlich viel'),
    SimpleTerm(value=5,
               title='sehr viel'),
    ])


MoreToLess = SimpleVocabulary([
    SimpleTerm(value=5,
               title='sehr wening'),
    SimpleTerm(value=4,
               title='ziemlich wenig'),
    SimpleTerm(value=3,
               title='etwas'),
    SimpleTerm(value=2,
               title='ziemlich viel'),
    SimpleTerm(value=1,
               title='sehr viel'),
    ])

@provider(IContextSourceBinder)
def quizz_choice(context):
    utils = getUtilitiesFor(IQuizz)
    return SimpleVocabulary([
        SimpleTerm(value=name, title=obj.__title__) for name, obj in utils
    ])


class ICriterias(IContent):
    pass


class ICriteria(IContent):

    title = schema.TextLine(
        title=_(u"Label"),
        required=True,
    )

    items = schema.Text(
        title=_(u"Please enter one criteria per line"),
        required=True,
    )


@implementer(ICriteria)
class Criteria(Base):

    __tablename__ = 'criterias'

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    items = Column('items', Text)
    company_id = Column(Integer, ForeignKey('companies.name'))

    @property
    def traversable_id(self):
        return str(self.id)


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

    courses = schema.Set(
        title=_(u"Courses"),
        required=False,
    )


def get_company_id(node):
    current = node
    while current is not None:
        if ICompany.providedBy(current):
            return current
        current = getattr(current, '__parent__', None)
    raise RuntimeError('No company found')


@provider(IContextSourceBinder)
def criterias_choice(context):
    session = get_session('school')
    company = get_company_id(context)
    criterias = session.query(Criteria).filter(
        Criteria.company_id == company.name)
    return SimpleVocabulary([
        SimpleTerm(value=c, token=c.id, title=c.title)
        for c in criterias])


class IClassSession(ILocation, IContent):
    
    startdate = schema.Date(
        title=_(u"Start date"),
        required=True,
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
        source=quizz_choice,
        required=True,
        )

    criterias = schema.Set(
        title=_(u"Criterias"),
        value_type=schema.Choice(source=criterias_choice),
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


criterias_table = Table('criterias_courses', Base.metadata,
    Column('courses_id', Integer, ForeignKey('courses.id')),
    Column('criterias_id', Integer, ForeignKey('criterias.id')),
    Column('company_id', String, ForeignKey('companies.name')),
)


@implementer(IQuizz, IStudent)
class Student(Base, Location):

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


@implementer(IClassSession)
class ClassSession(Base, Location):

    __tablename__ = 'sessions'
    model = Student

    id = Column('id', Integer, primary_key=True)
    startdate = Column('startdate', Date)
    company_id = Column(String, ForeignKey('companies.name'))
    course_id = Column(String, ForeignKey('courses.id'))
    
    _students = relationship(
        "Student", backref="session",
        collection_class=attribute_mapped_collection('access'))

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)

    def append(self, value):
        self._students[value.access] = value

    @property
    def enddate(self):
        return self.startdate + timedelta(days=21)

    @property
    def students(self):
        for key, student in self._students.items():
            student.__parent__ = self
            yield student
            
    def __getitem__(self, key):
        student = self._students[key]
        student.__parent__ = self
        return student

    @property
    def __name__(self):
        return str(self.id)

    @property
    def quizz_type(self):
        return self.course.quizz_type
    
    def generate_students(self, nb):
        for i in xrange(0, nb):
            access = self.model.generate_access()
            yield self.model(
                access=access,
                company_id=self.company_id,
                course_id=self.course.id,
                quizz_type=self.course.quizz_type)

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

    
@implementer(ICourse)
class Course(Base, Location):
    traversable('criterias', 'students', 'sessions')
    
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


@implementer(ICompany)
class Company(Base, Location):
    traversable('criterias')

    __tablename__ = 'companies'
    model = Course
    email = Column('email', String, primary_key=True)
    name = Column('name', String)
    password = Column('password', String)
    mnr = Column('mnr', String)
    activation = Column('activation', String)
    activated = Column('activated', DateTime)
    students = relationship("Student", backref="company")

    _courses = relationship(
        "Course", backref="company",
        collection_class=attribute_mapped_collection('id'))

    _criterias = relationship(
        "Criteria", backref=backref("company", uselist=False),
        collection_class=IntIds)

    @property
    def id(self):
        return self.name

    @property
    def criterias(self):
        self._criterias.__name__ = 'criterias'
        self._criterias.__parent__ = self
        directlyProvides(self._criterias, ICriterias)
        return self._criterias

    @property
    def courses(self):
        for key, course in self._courses.items():
            course.__parent__ = self
            yield course

    def __getitem__(self, key):
        try:
            course = self._courses[int(key)]
            course.__parent__ = self
            return course
        except (KeyError, ValueError):
            return None

    @property
    def __name__(self):
        return self.name

    @__name__.setter
    def __name__(self, value):
        pass


class CriteriaAnswer(Base):

    __tablename__ = 'criteria_answers'

    criteria_id = Column(Integer, ForeignKey('criterias.id'), primary_key=True)
    student_id = Column(String, ForeignKey('students.access'), primary_key=True)
    completion_date = Column('completion_date', DateTime,
                             default=datetime.utcnow)
    answer = Column('answer', String)

    criteria = relationship("Criteria", backref="answers")
    student = relationship("Student", backref="criterias")
