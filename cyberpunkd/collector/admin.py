# -*- coding: utf-8 -*-
from django.contrib import admin
from collector import models

admin.site.register(models.TwitterUser)
admin.site.register(models.Location)
admin.site.register(models.Tweet)
admin.site.register(models.TweetImage)
