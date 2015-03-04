import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rivers.settings")
from rivers import settings

from tos_import.models import Statement
from unittest import TestCase


class TestABC(TestCase):
    def test_some(self):
        print Statement.objects.using('default').count()
        print Statement.objects.using('slave').count()


        statement = Statement(
            date='2014-12-12',
            account_statement='',
            position_statement='',
            trade_activity='',
        )
        statement.save(using='slave')



        print Statement.objects.using('default').count()
        print Statement.objects.using('slave').count()

        Statement.objects.filter(date='2014-12-12').delete()

# todo: position set start here...