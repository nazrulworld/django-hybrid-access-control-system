# -*- coding: utf-8 -*-
# ++ This file `test_models.py` is generated at 11/16/16 6:19 AM ++
import pytest
from django.test import TestCase
#from hacs.models import *
from .path import FIXTURE_PATH
__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestHacsWorkflowModel(TestCase):
    """
    """
    fixtures = (FIXTURE_PATH / "testing_fixture.json", )

    def test_save(self):
        return True

