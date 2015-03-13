from django.test import TestCase
from position.classes.tests import create_filled_order
from tos_import.models import Statement, Underlying, Future, Forex
from tos_import.statement.statement_trade.models import TradeSummary


class TestUnitSetUpDB(TestCase):
    """
    Using unittest not django test
    """
    def setUp(self):
        """
        ready up all variables and test class
        """
        print '=' * 100
        print "<%s> currently run: %s" % (self.__class__.__name__, self._testMethodName)
        print '-' * 100 + '\n'

        self.spread = None

        # foreign key object
        self.statement = None
        self.trade_summary = None
        self.underlying = None

        # list use for determine spread
        self.spreads = list()
        self.sides = list()
        self.quantities = list()
        self.contracts = list()

        self.option_order = None

        self.create_filled_order = create_filled_order

        # noinspection PyBroadException
        try:
            self.statement = Statement(
                date='2015-01-01',
                account_statement='',
                position_statement='',
                trade_activity=''
            )
            self.statement.save()

            self.trade_summary = TradeSummary(
                date='2015-01-01',
                statement=self.statement
            )
            self.trade_summary.save()

            self.assertTrue(self.statement.id)
            self.assertTrue(self.trade_summary.id)

            self.underlying = Underlying(
                symbol='UNG1',  # add 1 as a test symbol
                company='United States Natural Gas Fund'
            )
            self.underlying.save()

            self.future = Future(
                symbol='ZWH5',
                lookup='ZW',
                description='WHEAT FUTURE',
                spc='1/50'
            )
            self.future.save()

            self.forex = Forex(
                symbol='USD/OJY',  # test symbol usd convert to my money
                description='DOLLARS/JINYANG SPOT'
            )
            self.forex.save()

            """
            print 'using statement: %s' % self.statement
            print 'using trade summary: %s' % self.trade_summary
            print 'using underlying: %s' % self.underlying
            print 'using future: %s' % self.future
            print 'using forex: %s' % self.forex
            print '-' * 80
            """
        except Exception:
            print 'Statement, trade_summary, underlying already exists...'

            self.statement = Statement.objects.get(date='2015-01-01')
            self.trade_summary = TradeSummary.objects.get(date='2015-01-01')
            self.underlying = Underlying.objects.get(symbol='UNG1')
            self.future = Future.objects.get(symbol='NGX5')
            self.forex = Forex.objects.get(symbol='USD/OJY')

    # noinspection PyBroadException
    def tearDown(self):
        """
        remove variables after test
        """
        print '\n' + '=' * 100 + '\n\n'

        print '-' * 80
        print 'remove statement, trade_summary, underlying...'
        try:
            self.statement.delete()
            self.trade_summary.delete()
            self.underlying.delete()
            self.future.delete()
            self.forex.delete()
        except Exception:
            Statement.objects.filter(date='2015-01-01').delete()
            TradeSummary.objects.filter(date='2015-01-01').delete()
            Underlying.objects.filter(symbol='UNG1').delete()
            Future.objects.filter(symbol='NGX5').delete()
            Forex.objects.filter(symbol='USD/OJY').delete()


