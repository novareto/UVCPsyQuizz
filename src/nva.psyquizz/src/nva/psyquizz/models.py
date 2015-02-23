# -*- coding: utf-8 -*-

import uuid

from . import Base
from cromlech.sqlalchemy import get_session
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import aliased
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from uvc.content.interfaces import IContent
from uvclight.directives import traversable
from zope.interface import Interface, implementer
from zope.location import ILocation, Location, LocationProxy
from zope import schema
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


TrueOrFalse = SimpleVocabulary([
    SimpleTerm(value=True,
               title='eher Ja'),
    SimpleTerm(value=False,
               title='eher Nein'),
    ])


class ICompany(ILocation, IContent):

    name = schema.TextLine(
        title=u"Firmenname",
        required=True,
        )

    password = schema.Password(
        title=u"Passwort",
        required=True,
        )

    courses = schema.Set(
        title=u"Courses",
        required=False,
        )


class ICourse(ILocation, IContent):

    name = schema.TextLine(
        title=u"Lehrgang",
        required=True,
        )
    
    students = schema.Set(
        title=u"Teilnehmer",
        required=False,
        )

    extra_questions = schema.Text(
        title=u"Zusatzfragen für diesen Lehrgang",
        description=u"Type your questions : one per line.",
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


class IQuizz(Interface):

    question1 = schema.Choice(
        title=u"1.1",
        description=u"Wird die auszuführende Arbeit von Ihnen selbst vorbereitet, organisiert und geprüft?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question2 = schema.Choice(
        title=u"1.2",
        description=u"Ist Ihre Tätigkeit abwechslungsreich?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question3 = schema.Choice(
        title=u"1.3",
        description=u"Haben Sie die Möglichkeit, eine wechselnde Körperhaltung einzunehmen?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question4 = schema.Choice(
        title=u"1.4",
        description=u"Erhalten Sie ausreichende Informationen zum eigenen Arbeitsbereich?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question5 = schema.Choice(
        title=u"1.5",
        description=u"Entspricht Ihre Qualifikation den Anforderungen, die durch die Tätigkeit gestellt werden?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question6 = schema.Choice(
        title=u"1.6",
        description=u"Ist die Tätigkeit frei von erhöhter Verletzungs- und Erkrankungsgefahr?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question7 = schema.Choice(
        title=u"1.7",
        description=u"Ist Ihre Tätigkeit frei von ungünstigen Arbeitsumgebungsbedingungen (z. B. Lärm, Klima, Gerüche)?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question8 = schema.Choice(
        title=u"1.8",
        description=u"Ist Ihre Tätigkeit frei von erhöhten emotionalen Anforderungen (z. B. im Publikumsverkehr)?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question9 = schema.Choice(
        title=u"1.9",
        description=u"Haben Sie Einfluss auf die Zeiteinteilung Ihrer Arbeit (z. B. Lage der Pausen, Arbeitstempo, Termine)?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question10 = schema.Choice(
        title=u"1.10",
        description=u"Haben Sie Einfluss auf die Vorgehensweise bei Ihrer Arbeit (z. B. Wahl der Arbeitsmittel/-methoden)?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question11 = schema.Choice(
        title=u"1.11",
        description=u"ErhaltenSieausreichendeInformationenzurEntwicklungdesBetriebes?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question12 = schema.Choice(
        title=u"2.1",
        description=u"Ist ein kontinuierliches Arbeiten ohne häufige Störungen möglich?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question13 = schema.Choice(
        title=u"2.2",
        description=u"Können Sie überwiegend ohne Zeit -und Termindruck arbeiten?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question14 = schema.Choice(
        title=u"2.3",
        description=u"Erhalten Sie ausreichende Rückmeldung (Anerkennung, Kritik, Beurteilung) über die eigene Leistung?",
        vocabulary=TrueOrFalse,
        required=True,
        )


    question15 = schema.Choice(
        title=u"2.4",
        description=u"Gibt es für Sie klare Entscheidungsstrukturen?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question16 = schema.Choice(
        title=u"2.5",
        description=u"Sind angeordnete Überstunden die Ausnahme?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question17 = schema.Choice(
        title=u"2.6",
        description=u"Wird Ihnen im Falle von Überstunden zeitnah Freizeitausgleich gewährt?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question18 = schema.Choice(
        title=u"3.1",
        description=u"Bietet Ihre Tätigkeit die Möglichkeit zur Zusammenarbeit mit Kolleginnen / Kollegen?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question19 = schema.Choice(
        title=u"3.2",
        description=u"Besteht ein positives soziales Klima?",
        vocabulary=TrueOrFalse,
        required=True,
        )

@implementer(IQuizz, IStudent)
class Student(Base, Location):

    __tablename__ = 'students'

    access = Column('access', String, primary_key=True)
    email = Column('email', String)
    course_id = Column(Integer, ForeignKey('courses.id'))
    company_id = Column(String, ForeignKey('companies.name'))

    # Quizz
    completion_date = Column('completion_date', DateTime)
    question1 = Column('question1', Boolean)
    question2 = Column('question2', Boolean)
    question3 = Column('question3', Boolean)
    question4 = Column('question4', Boolean)
    question5 = Column('question5', Boolean)
    question6 = Column('question6', Boolean)
    question7 = Column('question7', Boolean)
    question8 = Column('question8', Boolean)
    question9 = Column('question9', Boolean)
    question10 = Column('question10', Boolean)
    question11 = Column('question11', Boolean)
    question12 = Column('question12', Boolean)
    question13 = Column('question13', Boolean)
    question14 = Column('question14', Boolean)
    question15 = Column('question15', Boolean)
    question16 = Column('question16', Boolean)
    question17 = Column('question17', Boolean)
    question18 = Column('question18', Boolean)
    question19 = Column('question19', Boolean)
    extra_questions = Column('extra_questions', Text)

    @staticmethod
    def generate_access():
        return unicode(uuid.uuid4())

    def complete_quizz(self, **answers):
        self.completion_date = datetime.now()
        for key, value in answers.items():
            setattr(self, key, value)

    @property
    def __name__(self):
        return self.access

    @__name__.setter
    def __name__(self, value):
        pass



@implementer(ICourse)
class Course(Base, Location):

    __tablename__ = 'courses'
    model = Student
    db_key = 'access'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    company_id = Column(String, ForeignKey('companies.name'))
    extra_questions = Column('extra_questions', Text)

    _students = relationship(
        "Student", backref="course",
        collection_class=attribute_mapped_collection('access'))

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)

    def append(self, value):
        self._students[value.access] = value

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

    def generate_students(self, nb):
        for i in xrange(0, nb):
            access = self.model.generate_access()
            yield self.model(access=access, company_id=self.company_id)

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

    __tablename__ = 'companies'
    model = Course
    name = Column('name', String, primary_key=True)
    password = Column('password', String)
    students = relationship("Student", backref="company")

    _courses = relationship(
        "Course", backref="company",
        collection_class=attribute_mapped_collection('id'))

    @property
    def id(self):
        return self.name

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
