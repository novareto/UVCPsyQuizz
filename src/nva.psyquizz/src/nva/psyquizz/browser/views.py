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

from uvclight import Page, View
from uvclight import layer, title, name, context, get_template
from uvclight.auth import require
from zope.component import getUtilitiesFor
from zope.schema import getFieldsInOrder
from cromlech.sqlalchemy import get_session


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


class QuizzStats(object):

    def __init__(self, total, completed, extra_questions, quizz):
        self.quizz = quizz.__schema__
        self.completed = list(completed)
        self.percent_base = len(self.completed)
        self.missing = total - self.percent_base 
        self.extra_questions = extra_questions

    @staticmethod
    def compute(forms, fields):
        questions = OrderedDict()
        extras = OrderedDict()

        for form in forms:
            for field in fields:
                question = questions.setdefault(field, {})
                answer = getattr(form, field)
                stat = question.setdefault(answer, 0)
                question[answer] = stat + 1
            
            xa = json.loads(form.extra_questions)
            for title, answer in xa.items():
                question = extras.setdefault(title, {})
                stat = question.setdefault(answer, 0)
                question[answer] = stat + 1

        return questions, extras

    def get_answers(self):
        computed, extras = self.compute(self.completed, list(self.quizz))

        for key, field in getFieldsInOrder(self.quizz):
            question = {
                'title': self.quizz[key].title,
                'description': self.quizz[key].description,
                'answers': [],
                }
            for term in self.quizz[key].vocabulary:
                value = computed[key].get(term.value, 0)
                question['answers'].append({
                    'title': term.title,
                    'value': value,
                    'percent': float(value) / self.percent_base * 100
                    })
            yield question

        xq = set(self.extra_questions.strip().split('\n'))
        for title in xq:
            title = title.strip()
            if title == "":
                continue

            question = {
                'title': title,
                'description': '',
                'answers': [],
                }
            for term in TrueOrFalse:
                value = extras[title].get(term.value, 0)
                question['answers'].append({
                    'title': term.title,
                    'value': value,
                    'percent': float(value) / self.percent_base * 100
                    })
            yield question


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
        data = {}
        for name, quizz in getUtilitiesFor(IQuizz):
            students = session.query(Student).filter(
                Student.course_id == self.context.id).filter(
                    Student.company_id == self.context.company_id).filter(
                        Student.quizz_type == name).count()
            if students:
                answers = list(session.query(quizz).filter(
                    quizz.course_id == self.context.id).filter(
                        quizz.company_id == self.context.company_id))
                if answers:
                    data[name] = QuizzStats(
                        students, list(answers),
                        self.context.extra_questions, quizz)
        return data

    def display(self):
        for name, result in self.get_data().items():
            yield name, result.get_answers()


@menuentry(IContextualActionsMenu, order=20)
class CompanyResults(CompanyCourseResults):
    name('results')
    context(Company)
    layer(ICompanyRequest)
    require('manage.company')
    title(_(u'Company wide results'))

    def get_data(self):
        session = get_session('school')
        data = {}
        for name, quizz in getUtilitiesFor(IQuizz):
            students = session.query(Student).filter(
                Student.company_id == self.context.name).filter(
                    Student.quizz_type == name).count()

            if students:
                answers = list(session.query(quizz).filter(
                    quizz.company_id == self.context.name))

                if answers:
                    courses = session.query(Course).filter(
                        Course.company_id == self.context.name).filter(
                            Course.quizz_type == name)

                    extra_questions = "".join(
                        [course.extra_questions for course in courses])

                    data[name] = QuizzStats(
                        students, list(answers), extra_questions, quizz)
                    return data


@menuentry(IContextualActionsMenu, order=20)
class AllResults(CompanyCourseResults):
    name('results')
    context(admin.School)
    layer(ICompanyRequest)
    require('manage.school')
    title(_(u'Site wide results'))

    def update(self):
        session = get_session('school')
        data = {}
        for name, quizz in getUtilitiesFor(IQuizz):
            students = session.query(Student).filter(
                    Student.quizz_type == name).count()
            if students:
                answers = list(session.query(quizz))
                if answers:
                    courses = session.query(Course).filter(
                        Course.quizz_type == name)

                    extra_questions = "".join(
                        [course.extra_questions for course in courses])

                    data[name] = QuizzStats(
                        students, list(answers), extra_questions, quizz)
        return data

    def display(self):
        for name, result in self.get_data().items():
            yield name, result.get_answers()
