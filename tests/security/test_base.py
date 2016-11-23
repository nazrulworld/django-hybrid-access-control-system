# -*- coding: utf-8 -*-
# ++ This file `test_base.py` is generated at 11/23/16 5:42 PM ++
import pytest
from collections import defaultdict
from tests.path import FIXTURE_PATH
from django.test import TestCase
from django.db import connection
from hacs.db.models.base import HacsItemModel, HacsContainerModel, HacsUtilsModel
from django.contrib.auth import get_user_model

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"
