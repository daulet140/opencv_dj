# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import *

# admin.site.register(Person)
admin.site.register(Person, PersonAdmin)
