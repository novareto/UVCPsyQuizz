# -*- coding: utf-8 -*-

import json
import uvclight

from .forms import Stats
from ..apps import admin, anonymous
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..interfaces import IQuizzLayer
from ..interfaces import QuizzAlreadyCompleted, QuizzClosed
from ..models import IQuizz, TrueOrFalse
from ..models import Company, Course, Student, CriteriaAnswer
from collections import OrderedDict
from cromlech.sqlalchemy import get_session
from dolmen.menu import menuentry
from uvc.design.canvas.menus import INavigationMenu
from uvc.design.canvas import IAboveContent
from uvc.design.canvas import menus
from dolmen.message import receive
from dolmen.template import ITemplate
from grokcore.component import adapter, implementer
from nva.psyquizz import quizzjs
from uvc.design.canvas import IAboveContent, IBelowContent
from uvc.design.canvas import IContextualActionsMenu
from uvc.design.canvas import menus
from uvclight import Page, View, MenuItem
from uvclight import layer, title, name, menu, context, get_template
from uvclight.auth import require
from zope.component import getUtilitiesFor, getUtility
from zope.schema import getFieldsInOrder
from sqlalchemy import or_, and_


class FlashMessages(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(30)
    uvclight.name('messages')

    template = uvclight.get_template('flashmessages.cpt', __file__)

    def update(self):
        received = receive()
        if received is not None:
            self.messages = list(received)
        else:
            self.messages = []


@adapter(menus.IContextualActionsMenu, IQuizzLayer)
@implementer(ITemplate)
def object_template(context, request):
    return uvclight.get_template('objectmenu.cpt', __file__)


class CompanyCourseResults(uvclight.Viewlet):
    uvclight.viewletmanager(IBelowContent)
    uvclight.view(Stats)
    uvclight.name('results')

    template = uvclight.get_template('results.pt', __file__)

    colors = {
        1: 'rgba(215, 40, 40, 0.9)',
        2: 'rgba(212, 115, 60, 0.9)',
        3: 'rgba(255, 222, 30, 0.9)',
        4: 'rgba(201, 200, 0, 0.9)',
        5: 'rgba(58, 200, 0, 0.9)',
        }

    def students_ids(self, session):
        criterias = self.view.criterias
        if not criterias:
            return None

        students_ids = None
        for criteria_id, values in criterias.items():
            if values:
                query = session.query(CriteriaAnswer.student_id).filter(
                    CriteriaAnswer.criteria_id == criteria_id).filter(
                        CriteriaAnswer.answer.in_(list(values)))
                if students_ids is None:
                    students_ids = set([q[0] for q in query.all()])
                else:
                    students_ids &= set([q[0] for q in query.all()])

        return students_ids

    def get_data(self):
        session = get_session('school')
        quizz = getUtility(IQuizz, name=self.context.quizz_type)
        stats = quizz.__stats__
        data = {}

        restrict_students_id = self.students_ids(session)
        if restrict_students_id is not None and not restrict_students_id:
            # restriction removed ALL the results
            nb_students = 0
        else:
            # number of students
            students = session.query(Student).filter(
                Student.course_id == self.context.id).filter(
                    Student.company_id == self.context.company_id).filter(
                        Student.quizz_type == self.context.quizz_type)

            if restrict_students_id is not None:
                students.filter(Student.access.in_(restrict_students_id))

            nb_students = students.count()
                            
        if nb_students:
            answers = session.query(quizz).filter(
                quizz.course_id == self.context.id).filter(
                    quizz.company_id == self.context.company_id)

            if restrict_students_id is not None:
                answers.filter(quizz.student_id.in_(restrict_students_id))

            answers = list(answers)
    
            if answers:
                data[self.context.quizz_type] = stats(
                        nb_students, answers,
                        self.context.extra_questions, quizz)
        return data

    def display(self):
        quizzjs.need()
        for name, result in self.get_data().items():
            compute_chart = getattr(result, 'compute_chart', None)
            if compute_chart is None:
                yield name, {'results': result.get_answers(),
                             'users': None, 'chart': None}
            else:
                gbl, users = compute_chart()
                yield name, {'results': result.get_answers(),
                             'users': users,
                             'chart': gbl}

                
class Home(uvclight.MenuItem):
    uvclight.title(u'Home')
    uvclight.auth.require('zope.Public')
    uvclight.menu(INavigationMenu)

    @property
    def action(self):
        return self.view.application_url()
