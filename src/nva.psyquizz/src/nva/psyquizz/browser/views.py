# -*- coding: utf-8 -*-

import json

from collections import OrderedDict
from ..apps import admin, anonymous
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..interfaces import QuizzAlreadyCompleted, QuizzClosed
from ..models import IQuizz, Company, Course, Student, TrueOrFalse
from dolmen.menu import menuentry
from uvc.design.canvas import IContextualActionsMenu

from uvclight import Page, View, MenuItem
from uvclight import layer, title, name, menu, context, get_template
from uvclight.auth import require
from zope.component import getUtilitiesFor, getUtility
from zope.schema import getFieldsInOrder
from cromlech.sqlalchemy import get_session
from nva.psyquizz import quizzjs


class QuizzErrorPage(Page):
    name('')
    context(QuizzAlreadyCompleted)
    require('zope.Public')

    def render(self):
        return _(u"This quizz is already completed and therefore closed.")


class CourseExpiredPage(Page):
    name('')
    context(QuizzClosed)
    require('zope.Public')

    def render(self):
        return _(u"The course access is expired.")


class CriteriasAccess(MenuItem):
    context(Company)
    name('criteria')
    title('Criterias')
    layer(ICompanyRequest)
    menu(IContextualActionsMenu)

    url = '/criterias'

    
@menuentry(IContextualActionsMenu, order=20)
class CompanyCourseResults(Page):
    name('results')
    context(Course)
    layer(ICompanyRequest)
    require('manage.company')
    title(_(u'Results for the course'))

    template = get_template('results.pt', __file__)

    def filters(self, query):
        return query

    def get_data(self):
        session = get_session('school')
        quizz = getUtility(IQuizz, name=self.context.quizz_type)
        stats = quizz.__stats__
        data = {}
        
        # number of students
        students = session.query(Student).filter(
            Student.course_id == self.context.id).filter(
                Student.company_id == self.context.company_id).filter(
                    Student.quizz_type == self.context.quizz_type).count()
        if students:
            answers = list(session.query(quizz).filter(
                quizz.course_id == self.context.id).filter(
                    quizz.company_id == self.context.company_id))
            if answers:
                data[self.context.quizz_type] = stats(
                        students, list(answers),
                        self.context.extra_questions, quizz)
        return data

    def display(self):
        quizzjs.need()
        for name, result in self.get_data().items():
            compute_chart = getattr(result, 'compute_chart', None)
            if compute_chart is None:
                yield name, {'results': result.get_answers(), 'chart': None}
            else:
                chart = compute_chart()
                yield name, {'results': result.get_answers(), 'chart': chart}

# @menuentry(IContextualActionsMenu, order=20)
# class CompanyResults(CompanyCourseResults):
#     name('results')
#     context(Company)
#     layer(ICompanyRequest)
#     require('manage.company')
#     title(_(u'Company wide results'))

#     def get_data(self):
#         session = get_session('school')
#         data = {}
#         for name, quizz in getUtilitiesFor(IQuizz):
#             students = session.query(Student).filter(
#                 Student.company_id == self.context.name).filter(
#                     Student.quizz_type == name).count()

#             if students:
#                 answers = list(session.query(quizz).filter(
#                     quizz.company_id == self.context.name))

#                 if answers:
#                     courses = session.query(Course).filter(
#                         Course.company_id == self.context.name).filter(
#                             Course.quizz_type == name)

#                     extra_questions = "".join(
#                         [course.extra_questions for course in courses])

#                     data[name] = QuizzStats(
#                         students, list(answers), extra_questions, quizz)
#                     return data


# @menuentry(IContextualActionsMenu, order=20)
# class AllResults(CompanyCourseResults):
#     name('results')
#     context(admin.School)
#     layer(ICompanyRequest)
#     require('manage.school')
#     title(_(u'Site wide results'))

#     def update(self):
#         session = get_session('school')
#         data = {}
#         for name, quizz in getUtilitiesFor(IQuizz):
#             students = session.query(Student).filter(
#                     Student.quizz_type == name).count()
#             if students:
#                 answers = list(session.query(quizz))
#                 if answers:
#                     courses = session.query(Course).filter(
#                         Course.quizz_type == name)

#                     extra_questions = "".join(
#                         [course.extra_questions for course in courses])

#                     data[name] = QuizzStats(
#                         students, list(answers), extra_questions, quizz)
#         return data

#     def display(self):
#         for name, result in self.get_data().items():
#             yield name, result.get_answers()
