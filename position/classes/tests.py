from pprint import pprint
from unittest import TestCase
from os import environ
environ.setdefault("DJANGO_SETTINGS_MODULE", "rivers.settings")
# noinspection PyUnresolvedReferences
from rivers import settings
from tos_import.statement.statement_trade.models import *


class TestUnitSetUp(TestCase):
    def setUp(self):
        """
        ready up all variables and test class
        """
        print '=' * 100
        print "<%s> currently run: %s" % (self.__class__.__name__, self._testMethodName)
        print '-' * 100 + '\n'

    def tearDown(self):
        """
        remove variables after test
        """
        print '\n' + '=' * 100 + '\n\n'


class TestABC(TestUnitSetUp):
    def setUp(self):
        TestUnitSetUp.setUp(self)

        self.save_position = SavePosition()

    def test_save_all(self):
        """
        Test save position using data in db
        """
        for statement in Statement.objects.all()[:1]:
            print statement

            trade_summary = statement.tradesummary_set.first()
            """:type : TradeSummary """

            filled_orders = trade_summary.filledorder_set.all()

            for filled_order in filled_orders:
                """:type : FilledOrder"""
                #print filled_order.contract, filled_order.spread

                if filled_order.spread == 'STOCK' and filled_order.pos_effect == 'TO OPEN':
                    print filled_order.id, filled_order.spread, filled_order.pos_effect, filled_order.get_symbol()









        # todo: position set start here...





























