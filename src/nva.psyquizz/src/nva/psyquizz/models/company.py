# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from . import IntIds
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from uvclight.directives import traversable
from zope.interface import Interface, implementer, directlyProvides
from zope.location import Location
from .interfaces import ICompany, ICriterias
from uvc.content.interfaces import IDescriptiveSchema


@implementer(ICompany, IDescriptiveSchema)
class Company(Base, Location):
    traversable('criterias')

    __tablename__ = 'companies'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    mnr = Column('mnr', String)
    account_id = Column(String, ForeignKey('accounts.email'))
    
    students = relationship(
        "Student", backref="company")

    _courses = relationship(
        "Course", backref="company",
        collection_class=attribute_mapped_collection('id'))

    _criterias = relationship(
        "Criteria", backref=backref("company", uselist=False),
        collection_class=IntIds)

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
    def title(self):
        return self.name

    @property
    def __name__(self):
        return str(self.id)

    @__name__.setter
    def __name__(self, value):
        pass
