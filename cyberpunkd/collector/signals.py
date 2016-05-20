# -*- coding: utf-8 -*-
from __future__ import division, print_function

import asyncio
import datetime
from functools import partial
import json
import os
import shlex
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


with open(os.path.join(BASE_DIR, 'scraper.pid'), 'w') as pidfile:
    pidfile.write(str(os.getpid()))


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


def scrape_tweets():
    api = _get_api()
    hashtags = Location.objects.all().values_list('hashtag', flat=True)
    event_loop = asyncio.get_event_loop()

    for line in api.GetStreamFilter(track=hashtags):
        try:
            if 'in_reply_to_status_id' in line:
                event_loop.call_soon(insert_to_db(line))
        except twitter.TwitterError as e:
            post_slack(e.__repr__())
    try:
        event_loop.run_forever()
    finally:
        event_loop.close()


@receiver(post_save, sender=Location)
def sig_handler(sender, **kwargs):
    subprocess.call('{0}/kill_collector.sh'.format(BASE_DIR))


if __name__ == '__main__':
    scrape_tweets()
