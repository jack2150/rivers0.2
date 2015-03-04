import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rivers.settings")
from rivers import settings

from tos_import.models import Statement
from unittest import TestCase


class TestABC(TestCase):


    def test_some(self):
        pass


# todo: position set start here...