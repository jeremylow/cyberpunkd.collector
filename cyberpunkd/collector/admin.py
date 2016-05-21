# -*- coding: utf-8 -*-
from django.contrib import admin
from collector.models import TwitterUser, Location, Tweet

admin.site.register(TwitterUser)
admin.site.register(Location)
admin.site.register(Tweet)
