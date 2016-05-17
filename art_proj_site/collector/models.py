# -*- coding: utf-8 -*-
from django.db import models


class TwitterUser(models.Model):
    username = models.CharField(max_length=16)
    face_hash = models.TextField(blank=True)
    image = models.ImageField(null=True)


class Location(models.Model):
    loc_name = models.CharField(max_length=255)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)


class Tweet(models.Model):
    tweet_user = models.ForeignKey(TwitterUser)
    tweet_text = models.TextField()
    tweet_date = models.DateField()
    tweet_loc = models.OneToOneField(Location, null=True)
