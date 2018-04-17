# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.db import models
from django.utils import timezone


# Create your models here.

class Person(models.Model):
    name = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=timezone.now)

    def __int__(self):
        return self.id

    def __str__(self):
        return self.name


class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pub_date')
    list_filter = ('pub_date', 'name')
    fields = ['name']
