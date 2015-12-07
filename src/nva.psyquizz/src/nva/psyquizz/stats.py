# -*- coding: utf-8 -*-

import json
from collections import OrderedDict
from zope.schema import getFieldsInOrder
from .models import TrueOrFalse


def compute(forms, iface):
    questions = OrderedDict()
    extras = OrderedDict()
    users = []

    for form in forms:
        user = {}
        for field in list(iface):
            question = questions.setdefault(field, {})
            answer = getattr(form, field)
            stat = question.setdefault(answer, 0)
            question[answer] = stat + 1
            user[iface[field].title] = answer

        xa = json.loads(form.extra_questions)
        for title, answer in xa.items():
            question = extras.setdefault(title, {})
            stat = question.setdefault(answer, 0)
            question[answer] = stat + 1
            user[title] = answer

        users.append(user)

    return questions, extras, users


class QuizzStats(object):

    def __init__(self, total, completed, extra_questions, quizz):
        self.quizz = quizz.__schema__
        self.completed = list(completed)
        self.percent_base = len(self.completed)
        self.missing = total - self.percent_base 
        self.extra_questions = extra_questions
        self.computed, self.extras, self.users = compute(completed, self.quizz)

        criterias = {}
        for answer in completed:
            for criteria_answer in answer.student.criterias:
                criteria = criteria_answer.criteria
                criteria_data = criterias.setdefault(
                    criteria.id, {'title': criteria.title, 'answers': {}})
                criteria_data['answers'][criteria_answer.answer] = (
                    criteria_data['answers'].get(criteria_answer.answer, 0) + 1)

        self.criterias = criterias

    def get_answers(self):

        for key, field in getFieldsInOrder(self.quizz):
            question = {
                'title': self.quizz[key].title,
                'description': self.quizz[key].description,
                'answers': [],
                }
            for term in self.quizz[key].vocabulary:
                nb = self.computed[key].get(term.value, 0)
                question['answers'].append({
                    'title': term.title,
                    'nb': nb,
                    'value': term.value,
                    'percent': float(nb) / self.percent_base * 100
                    })
            yield question

        if self.extra_questions:
            xq = set(self.extra_questions.strip().split('\n'))
        else:
            xq = ()
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
                nb = self.extras[title].get(term.value, 0)
                question['answers'].append({
                    'title': term.title,
                    'nb': nb,
                    'value': term.value,
                    'percent': float(nb) / self.percent_base * 100
                    })
            yield question


class TrueFalseQuizzStats(QuizzStats):
    pass

            
class ChartedQuizzStats(QuizzStats):

    averages = {
        u'Handlungssspielraum': ('3.1', '3.2', '3.3'),
        u'Vielseitiges Arbeiten': ('1.1', '1.2', '1.3'),
        u'Ganzheitliches Arbeiten': ('1.4', '1.5'),
        u'Soziale Rückendeckung': ('3.4', '3.5', '3.6'),
        u'Zusammenarbeit': ('3.7', '3.8', '3.9'),
        u'Passende inhaltliche Arbeitsanforderungen': ('2.1', '2.2'),
        u'Passende mengenmäßige Arbeit': ('2.3', '2.4'),
        u'Passende Arbeitsabläufe': ('2.5', '2.6'),
        u'Passende Arbeitsumgebung': ('2.7', '2.8'),
        u'Information und Mitsprache': ('4.1', '4.2'),
        u'Entwicklungsmöglichkeiten': ('4.3', '4.4'),
        }

    determine_average = {}
    for label, questions in averages.items():
        for question in questions:
            determine_average[question] = label

    total = 0

    def compute_chart(self):
        answers = self.get_answers()
        averages = {}
        users_averages = {}

        for answer in answers:
            values = averages.setdefault(
                self.determine_average.get(answer['title']), {})
            values.setdefault('nb', 0)
            values.setdefault('sum', 0)
            for value_answer in answer['answers']:
                values['nb'] += value_answer['nb']
                values['sum'] += (value_answer['nb'] * value_answer['value'])

        for user in self.users:
            avg = user['averages'] = {}
            for title, ids in self.averages.items():
                group = users_averages.setdefault(title, {})
                group['total'] = group.get('total', 0) + 1
                avg = sum([user[id] for id in ids]) / len(ids)
                group[avg] = group.get(avg, 0) + 1

        for title, results in users_averages.items():
            for i in [1, 2, 3, 4, 5]:
                results[i] = results.get(i, 0)
                results[i] = results[i] / float(results['total']) * 100

        for data in averages.values():
            data['avg'] = float(data['sum']) / data['nb']

        return averages, users_averages
