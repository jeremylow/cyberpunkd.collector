# -*- coding: utf-8 -*-
from django.db import models


class TwitterUser(models.Model):
    username = models.CharField(max_length=16)
    face_hash = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True)

    def __str__(self):
        return "TwitterUser(name={0!r})".format(self.username)


class Location(models.Model):
    loc_name = models.CharField(max_length=255)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    hashtag = models.CharField(max_length=140, blank=True)

    def __str__(self):
        return "Location(name={0!r}, hashtag={1!r}, latitude={2}, longitude={3})".format(
            self.loc_name,
            self.hashtag,
            self.latitude,
            self.longitude)


class Tweet(models.Model):
    tweet_user = models.ForeignKey(TwitterUser)
    tweet_text = models.TextField()
    tweet_date = models.DateField()
    tweet_loc = models.ForeignKey(Location, null=True)

    def __str__(self):
        return "Tweet(tweet_user={0!r}, tweet_text={1!r}, tweet_date={2}, tweet_loc={3!r})".format(
            self.tweet_user.username,
            self.tweet_text,
            self.tweet_date,
            self.tweet_loc.loc_name)
