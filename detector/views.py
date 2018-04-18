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
        context['persons'] = persons.all().order_by('-pub_date')
        # last  days(24 hour)
        person_recently_up = persons.filter(pub_date__gte=time_24_hours_ago, name='up').count()
        context['personUpRecentlyCount'] = person_recently_up
        person_recently_down = persons.filter(pub_date__gte=time_24_hours_ago, name='down').count()
        context['personDownRecentlyCount'] = person_recently_down
        person_recently_count = person_recently_up + person_recently_down
        context['personAllRecentlyCount'] = person_recently_count
        # last seven days
        person_7_up = persons.filter(pub_date__gte=time_7_days_ago, name='up').count()
        context['personUpSevenCount'] = person_7_up
        person_7_down = persons.filter(pub_date__gte=time_7_days_ago, name='down').count()
        context['personDownSevenCount'] = person_7_down
        person_7_count = person_7_up + person_7_down
        context['personAllSevenCount'] = person_7_count
        # last thirty days
        person_30_up = persons.filter(pub_date__gte=time_30_days_ago, name='up').count()
        context['personUp30Count'] = person_30_up
        person_30_down = persons.filter(pub_date__gte=time_30_days_ago, name='down').count()
        context['personDown30Count'] = person_30_down
        person_30_count = person_30_up + person_30_down
        context['personAll30Count'] = person_30_count
        # last year
        person_year_up = persons.filter(pub_date__gte=time_year_ago, name='up').count()
        context['personUpYearCount'] = person_year_up
        person_year_down = persons.filter(pub_date__gte=time_year_ago, name='down').count()
        context['personDownYearCount'] = person_year_down
        person_year_count = person_year_up + person_year_down
        context['personAllYearCount'] = person_year_count
        # all
        person_all_up = persons.filter(name='up').count()
        context['personUpCount'] = person_all_up
        person_all_down = persons.filter(name='down').count()
        context['personDownCount'] = person_all_down
        person_all_count = person_all_up + person_all_down
        context['personAllCount'] = person_all_count

        static_30 = self.thirty_day_registrations()
        context['30_day'] = list(reversed(static_30['day']))
        context['30_day_count'] = list(reversed(static_30['count']))
        static_30_up = self.thirty_day_registrations_()
        context['30_day_up'] = list(reversed(static_30_up['day']))
        context['30_day_count_up'] = list(reversed(static_30_up['count']))
        static_30_down = self.thirty_day_registrations_('down')
        context['30_day_down'] = list(reversed(static_30_down['day']))
        context['30_day_count_down'] = list(reversed(static_30_down['count']))

        static_7 = self.seven()
        context['7_day'] = list(reversed(static_7['day']))
        context['7_day_count'] = list(reversed(static_7['count']))
        static_7_up = self.seven_()
        context['7_day_up'] = list(reversed(static_7_up['day']))
        context['7_day_count_up'] = list(reversed(static_7_up['count']))
        static_7_down = self.seven_()
        context['7_day_down'] = list(reversed(static_7_down['day']))
        context['7_day_count_down'] = list(reversed(static_7_down['count']))

        recent = self.lastday()
        context['day'] = list(reversed(recent['day']))
        context['day_count'] = list(reversed(recent['count']))
        recent_up = self.lastday_()
        context['day_up'] = list(reversed(recent_up['day']))
        context['day_up_count'] = list(reversed(recent_up['count']))
        recent_down = self.lastday_('down')
        context['day_down'] = list(reversed(recent_up['day']))
        context['day_down_count'] = list(reversed(recent_down['count']))

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

    def thirty_day_registrations_(self, x='up'):
        final_data = {}
        final_data['count'] = []
        final_data['day'] = []
        # time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        date = arrow.now()
        for day in xrange(0, 30):
            count = Person.objects.filter(
                pub_date__gte=date.floor('day').datetime,
                pub_date__lte=date.ceil('day').datetime,
                name=x
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

    def seven_(self, x='up'):
        final_data = {}
        final_data['count'] = []
        final_data['day'] = []
        # time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        date = arrow.now()
        for day in xrange(0, 7):
            count = Person.objects.filter(
                pub_date__gte=date.floor('day').datetime,
                pub_date__lte=date.ceil('day').datetime,
                name=x
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

        time_24_hours_ago = datetime.datetime.now()+datetime.timedelta(hours=5)
        for day in xrange(0, 24):
            count = Person.objects.filter(
                pub_date__gte=time_24_hours_ago,
                pub_date__lte=time_24_hours_ago + datetime.timedelta(hours=1)
            ).count()
            final_data['count'].append(count)
            time_24_hours_ago = time_24_hours_ago + datetime.timedelta(hours=-1)
        return final_data

    def lastday_(self, x='up'):
        final_data = {}
        final_data['count'] = []
        final_data['day'] = []

        time_24_hours_ago = datetime.datetime.now() + datetime.timedelta(hours=5)
        for day in xrange(0, 24):
            count = Person.objects.filter(
                pub_date__gte=time_24_hours_ago,
                pub_date__lte=time_24_hours_ago + datetime.timedelta(hours=1),
                name=x
            ).count()
            final_data['count'].append(count)
            time_24_hours_ago = time_24_hours_ago + datetime.timedelta(hours=-1)
        return final_data
