# -*- coding: utf-8 -*-

import json
from collections import OrderedDict
from zope.schema import getFieldsInOrder
from .models import TrueOrFalse


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
                nb = computed[key].get(term.value, 0)
                question['answers'].append({
                    'title': term.title,
                    'nb': nb,
                    'value': term.value,
                    'percent': float(nb) / self.percent_base * 100
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
                nb = extras[title].get(term.value, 0)
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
        u'Handlungssspielraum': ('1.1', '1.2', '1.3'),
        u'Vielseitiges Arbeiten': ('1.4', '1.5', '2.1'),
        u'Ganzheitliches Arbeiten': ('2.2', '2.3'),
        u'Soziale Rückendeckung': ('2.4', '2.5', '2.6'),
        u'Zusammenarbeit': ('2.7', '2.8', '3.1'),
        u'Passende inhaltliche Arbeitsanforderungen': ('3.2', '3.3'),
        u'Passende mengenmäßige Arbeit': ('3.4', '3.5'),
        u'Passende Arbeitsabläufe': ('3.6', '3.7'),
        u'Passende Arbeitsumgebung': ('3.8', '3.9'),
        u'Information und Mitsprache': ('4.1', '4.2'),
        u'Entwicklungsmöglichkeiten': ('4.3', '4.4'),
        }

    determine_average = {}
    for label, questions in averages.items():
        for question in questions:
            determine_average[question] = label

    def compute_chart(self):
        answers = self.get_answers()
        averages = {}

        for answer in answers:
            values = averages.setdefault(
                self.determine_average.get(answer['title']), {})
            values.setdefault('nb', 0)
            values.setdefault('sum', 0)
            for value_answer in answer['answers']:
                values['nb'] += value_answer['nb']
                values['sum'] += (value_answer['nb'] * value_answer['value'])

        for data in averages.values():
            data['avg'] = float(data['sum']) / data['nb']

        return averages
