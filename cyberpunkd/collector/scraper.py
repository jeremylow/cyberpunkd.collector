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

from __future__ import division, print_function

import curio
import datetime
import json
import os
import shlex
import signal
import subprocess
import sys
from tempfile import NamedTemporaryFile

import django
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
import twitter

import env

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyberpunkd.settings")
django.setup()

from collector.models import (  # NOQA
    TwitterUser,
    Tweet,
    TweetImage,
    Location)

__author__ = "Jeremy Low <jeremylow@gmail.com>"


def post_slack(msg):
    payload = {'text': msg}
    requests.post(
        env.SLACK_URL,
        json.dumps(payload),
        headers={'content-type': 'application/json'})


def _get_api():
    return twitter.Api(env.CONSUMER_KEY,
                       env.CONSUMER_SECRET,
                       env.ACCESS_TOKEN,
                       env.ACCESS_SECRET)


def http_to_file(url):
    _, ext = os.path.splitext(os.path.basename(url))
    data_file = NamedTemporaryFile(suffix=ext)
    req = requests.get(url, stream=True)
    data_file.write(req.raw.data)
    return data_file


def insert_to_db(data):
    status = twitter.Status.NewFromJsonDict(data)
    location = None
    images = []

    for hashtag in status.hashtags:
        ht = "#{0}".format(hashtag.text.lower())

        try:
            location = Location.objects.get(hashtag__iexact=ht)
        except Exception as e:
            post_slack(e.__repr__())

    if status.media:
        for image in status.media:
            images.append(image.media_url_https)
    else:
        return False

    if location is None:
        return False

    try:
        try:
            user = TwitterUser.objects.get(twitter_id=status.user.id)
        except ObjectDoesNotExist:
            user = TwitterUser(
                username=status.user.screen_name,
                twitter_id=status.user.id)
            user.save()

        tweet = Tweet(
            tweet_user=user,
            tweet_text=status.text,
            tweet_date=datetime.datetime.fromtimestamp(status.created_at_in_seconds),
            tweet_loc=location)
        tweet.save()

        if tweet and user and location:
            for image in images:
                temporary_file = http_to_file(image)

                tweet_image = TweetImage()
                tweet_image.tweet_user = user
                tweet_image.tweet = tweet
                tweet_image.image.save(os.path.basename(temporary_file.name), File(temporary_file))
                tweet_image.save()

    except Exception as e:
        print(e)


async def get_stream():
    api = _get_api()
    hashtags = Location.objects.all().values_list('hashtag', flat=True)
    print("Watching hashtags: {0}".format(", ".join(hashtags)))
    try:
        for line in api.GetStreamFilter(track=hashtags):
            try:
                if 'in_reply_to_status_id' in line:
                    await curio.run_in_process(insert_to_db, line)
            except twitter.TwitterError as e:
                post_slack(e.__repr__())
                continue
    except curio.CancelledError:
        pass


async def scrape_tweets():
    print("Started scraping, PID: ", os.getpid())
    with open(os.path.join(BASE_DIR, 'scraper.pid'), 'w') as pidfile:
        pidfile.write(str(os.getpid()))

    stream = await curio.spawn(get_stream())

    while True:
        await curio.SignalSet(signal.SIGPWR).wait()

        print("Restarting scraper")
        await stream.cancel()
        stream = await curio.spawn(get_stream())


if __name__ == '__main__':
    curio.run(scrape_tweets())
