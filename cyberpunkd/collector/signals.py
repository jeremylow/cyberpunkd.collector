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

import os
import signal
import sys

import django
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyberpunkd.settings")
django.setup()

from collector.models import (  # NOQA
    TwitterUser,
    Tweet,
    Location)

__author__ = "Jeremy Low <jeremylow@gmail.com>"


@receiver(post_delete, sender=Location)
@receiver(post_save, sender=Location)
def sig_handler(sender, **kwargs):
    with open('{0}/scraper.pid'.format(BASE_DIR), 'r') as f:
        pid = int(f.read())

    print("Sending SIGPWR")
    os.kill(pid, signal.SIGPWR)
