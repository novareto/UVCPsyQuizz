# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from nva.psyquizz.sqlutils import IntIds
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from uvclight.directives import traversable
from zope.interface import Interface, implementer
from zope.location import Location
from .interfaces import ICompany


@implementer(ICompany)
class Company(Base, Location):
    traversable('criterias')
    
    __tablename__ = 'companies'

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
