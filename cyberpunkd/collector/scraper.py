# -*- coding: utf-8 -*-
from __future__ import division, print_function

import curio
import datetime
import json
import os
import shlex
import signal
import subprocess
import sys

import django
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
    Location)


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


def insert_to_db(data):
    status = twitter.Status.NewFromJsonDict(data)
    location = None

    for hashtag in status.hashtags:
        ht = "#{0}".format(hashtag.text.lower())

        try:
            location = Location.objects.get(hashtag__iexact=ht)
        except Exception as e:
            post_slack(e.__repr__())

    if location is None:
        return False

    try:
        user = TwitterUser(username=status.user.screen_name,
                           face_hash=None,
                           image=None)
        user.save()
        tweet = Tweet(tweet_user=user,
                      tweet_text=status.text,
                      tweet_date=datetime.datetime.fromtimestamp(status.created_at_in_seconds),
                      tweet_loc=location)
        tweet.save()
    except Exception as e:
        post_slack(e.__repr__())


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
