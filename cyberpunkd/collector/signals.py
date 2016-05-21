# -*- coding: utf-8 -*-
from __future__ import division, print_function

import os
import signal
import sys

import django
from django.db.models.signals import post_save
from django.dispatch import receiver

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyberpunkd.settings")
django.setup()

from collector.models import (  # NOQA
    TwitterUser,
    Tweet,
    Location)


@receiver(post_save, sender=Location)
def sig_handler(sender, **kwargs):
    with open('{0}/scraper.pid'.format(BASE_DIR), 'r') as f:
        pid = int(f.read())

    print("Sending SIGPWR")
    os.kill(pid, signal.SIGPWR)
