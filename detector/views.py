# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Person

import datetime
import itertools
import arrow

datetime.datetime.now(tz=timezone.utc)


@login_required
def index(request):
    time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    time_7_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    time_30_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    time_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)

    persons = Person.objects
    person_all = persons.all().count()

    person_recently = persons.filter(pub_date__gte=time_24_hours_ago)

    person_recently_count = person_recently.count()

    person_7 = persons.filter(pub_date__gte=time_7_days_ago)
    person_7_count = person_7.count()

    person_30 = persons.filter(pub_date__gte=time_30_days_ago)
    person_30_count = person_30.count()

    person_year = persons.filter(pub_date__gte=time_year_ago)
    person_year_count = person_year.count()

    return render(
        request,
        'detector/index.html',
        context={'all': person_all,
                 'person_recently_count': person_recently_count,
                 'person_7_count': person_7_count,
                 'person_30_count': person_30_count,
                 'person_year_count': person_year_count,
                 },
    )


@method_decorator(login_required, name='dispatch')
class AnalyticsIndexView(TemplateView):
    template_name = 'detector/index.html'

    def get_context_data(self, **kwargs):
        context = super(AnalyticsIndexView, self).get_context_data(**kwargs)
        time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=1)
        time_7_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        time_30_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        time_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)

        persons = Person.objects

        person_recently = persons.filter(pub_date__gte=time_24_hours_ago)
        person_recently_count = person_recently.count()

        person_7 = persons.filter(pub_date__gte=time_7_days_ago)
        person_7_count = person_7.count()

        person_30 = persons.filter(pub_date__gte=time_30_days_ago)
        person_30_count = person_30.count()

        person_year = persons.filter(pub_date__gte=time_year_ago)
        person_year_count = person_year.count()

        person_all = persons.all().count()

        static_30 = self.thirty_day_registrations()
        static_7 = self.seven()
        recent = self.lastday()

        context['30_day'] = list(reversed(static_30['day']))
        context['30_day_count'] = list(reversed(static_30['count']))

        context['7_day'] = list(reversed(static_7['day']))
        context['7_day_count'] = list(reversed(static_7['count']))

        context['day'] = list(reversed(recent['day']))
        context['day_count'] = list(reversed(recent['count']))

        context['all'] = person_all
        context['persons'] = persons.all().order_by('-pub_date')
        context['person_recently_count'] = person_recently_count
        context['person_7_count'] = person_7_count
        context['person_30_count'] = person_30_count
        context['person_year_count'] = person_year_count
        return context

    def thirty_day_registrations(self):
        final_data = {}
        final_data['count'] = []
        final_data['day'] = []
        # time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        date = arrow.now()
        for day in xrange(0, 30):
            count = Person.objects.filter(
                pub_date__gte=date.floor('day').datetime,
                pub_date__lte=date.ceil('day').datetime
            ).count()
            final_data['count'].append(count)
            # final_data['day'].append(str('%s.%s.%s' % (date.day, date.month,date.year)))
            final_data['day'].append(date.day)
            date = date.replace(days=-1)

        return final_data

    def seven(self):
        final_data = {}
        final_data['count'] = []
        final_data['day'] = []
        # time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        date = arrow.now()
        for day in xrange(0, 7):
            count = Person.objects.filter(
                pub_date__gte=date.floor('day').datetime,
                pub_date__lte=date.ceil('day').datetime
            ).count()
            final_data['count'].append(count)
            # final_data['day'].append(str('%s.%s.%s' % (date.day, date.month,date.year)))
            final_data['day'].append(date.day)
            date = date.replace(days=-1)
        return final_data

    def lastday(self):
        final_data = {}
        final_data['count'] = []
        final_data['day'] = []

        time_24_hours_ago = datetime.datetime.now()
        for day in xrange(0, 24):
            count = Person.objects.filter(
                pub_date__gte=time_24_hours_ago,
                pub_date__lte=time_24_hours_ago + datetime.timedelta(hours=1),
            ).count()
            final_data['count'].append(count)
            time_24_hours_ago = time_24_hours_ago + datetime.timedelta(hours=-1)
        return final_data
