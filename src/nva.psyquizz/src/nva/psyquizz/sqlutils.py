# -*- coding: utf-8 -*-

from sqlalchemy.orm.collections import collection
from zope.location import ILocation, Location, LocationProxy, locate


class IntIds(Location):

    def __init__(self):
        self._data = {}

    @collection.appender
    def _append(self, child):
        self._data[child.id] = child

    def __setitem__(self, id, child):
        self._append(child)

    def __getitem__(self, id):
        try:
            obj = self._data[int(id)]
            if obj is not None:
                if not ILocation.providedBy(obj):
                    return LocationProxy(obj, self, id)
                else:
                    obj.__parent__ = self
                    return obj
        except:
            pass
        raise KeyError(id)

    @collection.remover
    def _remove(self, child):
        del self._data[child.id]

    @collection.iterator
    def __iter__(self):
        return self._data.itervalues()

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self._data)
