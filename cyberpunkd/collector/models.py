# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models

__author__ = "Jeremy Low <jeremylow@gmail.com>"


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
