# noinspection PyUnresolvedReferences
import position.classes.ready_django
from django.utils import timezone
from unittest import TestCase
from position.classes.manager import PositionSetManager
from position.models import PositionContext, PositionSet
from tos_import.models import Statement, Underlying, Future, Forex
from tos_import.statement.statement_account.models import ProfitLoss
from tos_import.statement.statement_position.models import PositionInstrument, PositionFuture, PositionForex
from tos_import.statement.statement_trade.models import TradeSummary
from tos_import.statement.statement_trade.models import FilledOrder
from django.core.exceptions import ObjectDoesNotExist


def create_filled_order(trade_summary, spread, contract,
                        underlying=None, future=None, forex=None,
                        side=0, quantity=0, strike=0.0,
                        price=14.31, net_price=14.31):
    """
    Create filled order that use for testing, can be stock or option
    :param trade_summary: TradeSummary
    :param underlying: Underlying
    :param spread: str
    :param contract: str
    :param side: str ('BUY', 'SELl')
    :param quantity: int
    """
    filled_order = FilledOrder(
        trade_summary=trade_summary,
        underlying=underlying,
        future=future,
        forex=forex,
        exec_time=timezone.now(),
        spread=spread,
        side=side,
        quantity=quantity,
        pos_effect='TO OPEN',
        expire_date=None,
        strike=strike,
        contract=contract,
        price=price,
        net_price=net_price,
        order='LMT'
    )
    filled_order.save()

    return filled_order


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


class TestUnitSetUpPrepare(TestUnitSetUp):
    """
    Using unittest not django test
    """
    def setUp(self):
        """
        ready up all variables and test class
        """
        TestUnitSetUp.setUp(self)

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

        self.filled_order = None

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

            print 'using statement: %s' % self.statement
            print 'using trade summary: %s' % self.trade_summary
            print 'using underlying: %s' % self.underlying
            print 'using future: %s' % self.future
            print 'using forex: %s' % self.forex
            print '-' * 80
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
        TestUnitSetUp.tearDown(self)

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


class TestPositionSetPrepare(TestUnitSetUp):
    def setUp(self):
        TestUnitSetUp.setUp(self)

        self.position_set = None

        self.position_sets = list()
        self.position_instruments = list()
        self.position_futures = list()
        self.position_forexs = list()
        self.profits_losses = list()

    def tearDown(self):
        TestUnitSetUp.tearDown(self)

        # remove foreign keys
        for position_instrument in self.position_instruments:
            position_instrument.position_set = None
            position_instrument.save()

        for position_future in self.position_futures:
            position_future.position_set = None
            position_future.save()

        for position_forexs in self.position_forexs:
            position_forexs.position_set = None
            position_forexs.save()

        for profit_loss in self.profits_losses:
            profit_loss.position_set = None
            profit_loss.save()

        # remove position sets
        if self.position_set:
            self.position_sets.append(self.position_set)

        for position_set in self.position_sets:
            if position_set.context:
                position_set.context.break_even.delete()
                position_set.context.start_profit.delete()
                position_set.context.start_loss.delete()
                position_set.context.max_profit.delete()
                position_set.context.max_loss.delete()
                position_set.context.delete()
            elif position_set.contexts:
                position_set.contexts.left.break_even.delete()
                position_set.contexts.left.start_profit.delete()
                position_set.contexts.left.start_loss.delete()
                position_set.contexts.left.max_profit.delete()
                position_set.contexts.left.max_loss.delete()
                position_set.contexts.left.delete()
                position_set.contexts.right.break_even.delete()
                position_set.contexts.right.start_profit.delete()
                position_set.contexts.right.start_loss.delete()
                position_set.contexts.right.max_profit.delete()
                position_set.contexts.right.max_loss.delete()
                position_set.contexts.right.delete()

            position_set.delete()

            # print PositionSet.objects.count()


class TestSavePositionSet(TestPositionSetPrepare):
    def setUp(self):
        TestPositionSetPrepare.setUp(self)

        try:
            trade_summary = TradeSummary.objects.get(date='2015-01-29')
            self.filled_orders = FilledOrder.objects.filter(trade_summary=trade_summary).all()
        except ObjectDoesNotExist:
            self.skipTest("Please use 'Unittest' for testing existing db testing.\n")
            raise ObjectDoesNotExist()

        self.save_manager = PositionSetManager.save(
            filled_orders=self.filled_orders
        )

    def test_get_underlying_symbols(self):
        """
        Test get underlying symbols from filled orders
        """
        underlying_symbols = self.save_manager.get_underlying_symbols()

        print 'Underlying symbol:'
        print underlying_symbols
        self.assertEqual(type(underlying_symbols), list)
        self.assertGreaterEqual(len(underlying_symbols), 1)

        for symbol in underlying_symbols:
            self.assertTrue(Underlying.objects.filter(symbol=symbol).exists())

    def test_get_future_symbols(self):
        """
        Test get underlying symbols from filled orders
        """
        future_symbols = self.save_manager.get_future_symbols()

        print 'Underlying symbol:'
        print future_symbols
        self.assertEqual(type(future_symbols), list)
        self.assertGreaterEqual(len(future_symbols), 1)

        for symbol in future_symbols:
            self.assertTrue(Future.objects.filter(symbol=symbol).exists())

    def test_get_forex_symbols(self):
        """
        Test get underlying symbols from filled orders
        """
        forex_symbols = self.save_manager.get_forex_symbols()

        print 'Underlying symbol:'
        print forex_symbols
        self.assertEqual(type(forex_symbols), list)
        self.assertGreaterEqual(len(forex_symbols), 1)

        for symbol in forex_symbols:
            self.assertTrue(Forex.objects.filter(symbol=symbol).exists())

    def test_create_set(self):
        """
        Test create position context using filled order
        """
        filled_orders = self.filled_orders.filter(underlying__symbol='AAPL')

        print 'run create set...'
        self.position_set = self.save_manager.create_set(
            filled_orders=filled_orders
        )

        self.assertTrue(self.position_set.id)
        self.assertTrue(self.position_set.underlying.id)
        self.assertFalse(self.position_set.future)
        self.assertFalse(self.position_set.forex)
        self.assertEqual(self.position_set.name, 'SPREAD')
        self.assertEqual(self.position_set.spread, 'SHORT_CALL_VERTICAL')
        self.assertEqual(type(self.position_set.context), PositionContext)

        print 'position set output:'
        print 'position_set id: %d' % self.position_set.id
        print 'position_set underlying: %s' % self.position_set.underlying
        print 'position_set name: %s' % self.position_set.name
        print 'position_set spread: %s' % self.position_set.spread
        print 'position_set context: %s' % self.position_set.context

    def test_save_underlying_position_set(self):
        """
        Test save underlying position set into db
        """
        self.position_sets = self.save_manager.save_underlying_position_set()

        self.assertEqual(type(self.position_sets), list)
        self.assertGreaterEqual(len(self.position_sets), 1)

        for position_set in self.position_sets:
            print position_set
            self.assertTrue(position_set.id)

            self.assertTrue(position_set.underlying.id)
            self.assertFalse(position_set.future)
            self.assertFalse(position_set.forex)
            self.assertEqual(type(position_set.context), PositionContext)

            self.assertNotIn(position_set.name, ['FUTURE', 'FOREX'])
            self.assertNotIn('FUTURE', position_set.spread)
            self.assertNotIn('FOREX', position_set.spread)

    def test_save_future_position_set(self):
        """
        Test save underlying position set into db
        """
        self.position_sets = self.save_manager.save_future_position_set()

        self.assertEqual(type(self.position_sets), list)
        self.assertGreaterEqual(len(self.position_sets), 1)

        for position_set in self.position_sets:
            print position_set
            self.assertTrue(position_set.id)

            self.assertFalse(position_set.underlying)
            self.assertTrue(position_set.future)
            self.assertFalse(position_set.forex)
            self.assertEqual(type(position_set.context), PositionContext)

            self.assertIn('FUTURE', position_set.name)
            self.assertIn('FUTURE', position_set.spread)

    def test_save_forex_position_set(self):
        """
        Test save underlying position set into db
        """
        self.position_sets = self.save_manager.save_forex_position_set()

        self.assertEqual(type(self.position_sets), list)
        self.assertGreaterEqual(len(self.position_sets), 1)

        for position_set in self.position_sets:
            print position_set
            self.assertTrue(position_set.id)

            self.assertFalse(position_set.underlying)
            self.assertFalse(position_set.future)
            self.assertTrue(position_set.forex.id)
            self.assertEqual(type(position_set.context), PositionContext)

            self.assertIn('FOREX', position_set.name)
            self.assertIn('FOREX', position_set.spread)

    def test_start(self):
        """
        Test save all position set using filled orders
        """
        self.position_sets = self.save_manager.start()

        self.assertEqual(type(self.position_sets), list)

        for position_set in self.position_sets:
            print position_set

            self.assertTrue(position_set.id)


class TestUpdatePositionSet(TestPositionSetPrepare):
    def setUp(self):
        TestPositionSetPrepare.setUp(self)

        self.update_manager = PositionSetManager.update()

        # ready up
        filled_orders = FilledOrder.objects.filter(trade_summary__date='2015-01-29')
        if filled_orders.exists():
            filled_orders = filled_orders.all()
        else:
            self.skipTest("Please use 'Unittest' for testing existing db testing.\n")
            raise ObjectDoesNotExist()

        self.position_sets = PositionSetManager.save(filled_orders=filled_orders).start()

        # get position instrument
        self.position_instruments = PositionInstrument.objects.filter(
            position_summary__date='2015-01-29'
        ).all()

        # get position future
        self.position_futures = PositionFuture.objects.filter(
            position_summary__date='2015-01-29'
        )

        # get position forex
        self.position_forexs = PositionForex.objects.filter(
            position_summary__date='2015-01-29'
        )

        # get profit loss
        self.profits_losses = ProfitLoss.objects.filter(
            account_summary__date='2015-01-29'
        )

        print 'ready up...'
        print 'position_set count: %d' % len(self.position_sets)
        print '.' * 80

    def update_test(self, position_items, test_method):
        """
        Test method use for update foreign key position set
        """
        for position_item in position_items:
            self.assertFalse(position_item.position_set)

        print 'run update instruments...'
        position_items = getattr(self.update_manager, test_method)(
            position_items
        )

        for position_item in position_items:
            print '%s' % position_item
            print 'Foreign Key: %s' % position_item.position_set
            print '.' * 60

            self.assertTrue(position_item.position_set.id)
            self.assertEqual(type(position_item.position_set), PositionSet)

    def test_update_position_instruments(self):
        """
        Test update position instruments that set position set
        """
        self.update_test(
            self.position_instruments,
            'update_position_instruments'
        )

    def test_update_position_futures(self):
        """
        Test update position futures that set position set
        """
        self.update_test(
            self.position_futures,
            'update_position_futures'
        )

    def test_update_position_forexs(self):
        """
        Test update position forex to set position set
        """
        self.update_test(
            self.position_forexs,
            'update_position_forexs'
        )

    def test_update_profits_losses(self):
        """
        Test update profit loss to set position set
        """
        self.update_test(
            self.profits_losses,
            'update_profits_losses'
        )

























