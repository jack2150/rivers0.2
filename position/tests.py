from django.test import SimpleTestCase
from tos_import.classes.test.__test import SetUpTestDB, TestSetUp
from tos_import.models import Statement


class SavePosition(object):
    """
    A position come with
    1. a position start
    1.1 filled order 'to open'
    1.2 position statement record
    1.3 account statement record

    1.* either can be a equity, option, or spread
        (future and forex skip, build later)

    end. with or without filled order 'to close'
    """
    def __init__(self, statement):
        """
        :param statement: Statement
        """
        self.statement = statement

    def start(self):

        return 123


class TestSavePosition(SimpleTestCase):
    def test_123(self):
        """
        Test start that insert all data into models
        """
        statement = Statement.objects.create(
            date='2014-12-12',
            account_statement='',
            position_statement='',
            trade_activity='',
        )

        print Statement.objects.using('default').count()
        #print Statement.objects.using('slave').count()



    def test_222(self):
        print Statement.objects.count()


# todo: try fixtures and master/slave, very slow, try other sql option
