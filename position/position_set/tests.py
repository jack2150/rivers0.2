# noinspection PyUnresolvedReferences
import position.classes.ready_django
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from position.classes.tests import TestUnitSetUp
from position.position_set.manager import PositionSetManager
from position.position_set.controller import PositionSetController
from position.models import PositionSet, StartProfit
from tos_import.models import Underlying
from tos_import.statement.statement_trade.models import FilledOrder


class TestPositionSetCls(TestUnitSetUp):
    def ready_position_set(self, symbol, investment, date='2015-01-29'):
        """
        get filled orders from db
        :param symbol: str
        :param investment: str
        """
        query = Q()
        if investment == 'underlying':
            query = Q(underlying__symbol=symbol)
        elif investment == 'future':
            query = Q(future__symbol=symbol)
        elif investment == 'forex':
            query = Q(forex__symbol=symbol)

        filled_orders = FilledOrder.objects.filter(
            Q(trade_summary__date=date) & query
        )

        if filled_orders.exists():
            self.filled_orders = filled_orders.all()
            self.position_set = PositionSet()
            self.manager = PositionSetManager(self.position_set)
        else:
            self.skipTest("Please use 'Unittest' for testing existing db testing.\n")
            raise ObjectDoesNotExist()

    def setUp(self):
        TestUnitSetUp.setUp(self)

        self.filled_orders = None
        self.position_set = None

        # foreign keys
        self.position_instruments = list()
        self.profits_losses = list()
        self.position_forexs = list()
        self.position_forexs = list()

    def tearDown(self):
        """
        Clean up database...
        """
        TestUnitSetUp.tearDown(self)

        if self.position_set is not None:
            self.position_set = self.position_set
            """:type: PositionSet"""

            self.position_set.filledorder_set.update(position_set=None)
            self.position_set.positioninstrument_set.update(position_set=None)
            self.position_set.positionfuture_set.update(position_set=None)
            self.position_set.positionforex_set.update(position_set=None)
            self.position_set.profitloss_set.update(position_set=None)

            if self.position_set.id:
                self.position_set.delete()


class TestPositionSetManager(TestPositionSetCls):
    def setUp(self):
        TestPositionSetCls.setUp(self)

        self.ready_position_set(symbol='AAPL', investment='underlying')

    def test_context_item_adds(self):
        """
        Test add foreign key items
        """
        start_profit = StartProfit(price=1.11, condition='>')
        self.manager.contexts = dict(start_profits=[start_profit])
        print 'start_profit: %s' % start_profit
        self.assertFalse(start_profit.id)

        self.manager.context_item_adds(
            name='start_profits', fk_set='startprofit_set'
        )

        print 'start_profit id: %d' % start_profit.id
        print 'position_set id %s' % self.manager.position_set.id
        self.assertTrue(start_profit.id)
        self.assertEqual(start_profit.position_set, self.manager.position_set)
        self.assertFalse(self.manager.position_set.id)

    def test_get_filled_orders(self):
        """
        Test get filled orders into set manager using property
        """
        print 'run set filled_orders...'
        self.manager.filled_orders = self.filled_orders

        print 'get filled_orders: %s' % self.manager.filled_orders

        self.assertEqual(self.manager.filled_orders, self.filled_orders)

    def test_set_filled_orders(self):
        """
        Test set filled orders into position set values
        """
        self.manager.filled_orders = self.filled_orders

        print self.manager.position_set.underlying
        self.assertTrue(self.manager.position_set.underlying)
        self.assertEqual(type(self.manager.position_set.underlying), Underlying)
        self.assertEqual(self.manager.position_set.underlying.symbol, 'AAPL')
        self.assertFalse(self.manager.position_set.future)
        self.assertFalse(self.manager.position_set.forex)

        print self.manager.position_set.name
        self.assertEqual(self.manager.position_set.name, 'SPREAD')
        self.assertEqual(type(self.manager.position_set.name), str)

        print self.manager.position_set.spread
        self.assertEqual(self.manager.position_set.spread, 'SHORT_CALL_VERTICAL')
        self.assertEqual(type(self.manager.position_set.spread), str)

        print self.manager.position_set.status
        self.assertEqual(self.manager.position_set.status, 'OPEN')
        self.assertEqual(type(self.manager.position_set.status), str)

        self.assertFalse(self.position_set.breakeven_set.exists())
        self.assertFalse(self.position_set.startprofit_set.exists())
        self.assertFalse(self.position_set.startloss_set.exists())
        self.assertFalse(self.position_set.maxprofit_set.exists())
        self.assertFalse(self.position_set.maxloss_set.exists())

    def test_set_then_save(self):
        """
        Test after set filled_orders, save position_set
        """
        print 'set filled_orders to position_set manager...'
        self.position_set.manager.filled_orders = self.filled_orders

        print 'run position_set save...'
        self.position_set.save()

        print self.position_set
        print '.' * 60
        print 'position set output:'
        print 'position_set id: %d' % self.position_set.id
        print 'position_set underlying: %s' % self.position_set.underlying
        print 'position_set name: %s' % self.position_set.name
        print 'position_set spread: %s' % self.position_set.spread

        print 'position_set breakeven_set: %s' % self.position_set.breakeven_set.all()
        print 'position_set startprofit_set: %s' % self.position_set.startprofit_set.all()
        print 'position_set startloss_set: %s' % self.position_set.startloss_set.all()
        print 'position_set maxprofit_set: %s' % self.position_set.maxprofit_set.all()
        print 'position_set maxloss_set: %s' % self.position_set.maxloss_set.all()

        self.assertTrue(self.position_set.id)
        self.assertTrue(self.position_set.breakeven_set.exists())
        self.assertTrue(self.position_set.startprofit_set.exists())
        self.assertTrue(self.position_set.startloss_set.exists())
        self.assertTrue(self.position_set.maxprofit_set.exists())
        self.assertTrue(self.position_set.maxloss_set.exists())

    def test_update_fk_filled_orders(self):
        """
        Test update filled_orders
        """
        print 'ready up...'
        self.manager.filled_orders = self.filled_orders
        self.position_set.save()

        ref = self.manager.update_foreign_keys()

        self.filled_orders = ref['filled_orders']

        # update filled_orders position_set
        for filled_order in self.filled_orders:
            print filled_order, filled_order.pos_effect
            print filled_order.position_set

            self.assertTrue(filled_order.position_set)
            self.assertEqual(filled_order.position_set, self.position_set)

    def test_update_fk_underlying(self):
        """
        Test update position instruments
        """
        print 'ready up...'
        self.manager.filled_orders = self.filled_orders
        self.position_set.save()

        ref = self.manager.update_foreign_keys()

        self.filled_orders = ref['filled_orders']
        self.position_instruments = ref['position_instruments']
        self.profits_losses = ref['profits_losses']

        for position_instrument in self.position_instruments:
            print position_instrument
            print position_instrument.position_set
            self.assertEqual(position_instrument.position_set, self.position_set)

        for profit_loss in self.profits_losses:
            print profit_loss
            print profit_loss.position_set
            self.assertEqual(profit_loss.position_set, self.position_set)

    def test_update_fk_future(self):
        """
        Test update position instruments
        """
        print 'ready up...'
        self.ready_position_set(symbol='/ZWH5', investment='future')

        self.position_set.manager.filled_orders = self.filled_orders
        self.position_set.save()

        print 'run update_fk...'
        ref = self.position_set.manager.update_foreign_keys()

        self.filled_orders = ref['filled_orders']
        self.position_forexs = ref['position_futures']
        self.profits_losses = ref['profits_losses']

        for position_future in self.position_forexs:
            print position_future
            print position_future.position_set
            self.assertEqual(position_future.position_set, self.position_set)

        print '.' * 60

        for profit_loss in self.profits_losses:
            print profit_loss
            print profit_loss.position_set
            self.assertEqual(profit_loss.position_set, self.position_set)

    def test_update_fk_forex(self):
        """0
        Test update position forexs
        """
        print 'ready up...'
        self.ready_position_set(symbol='USD/JPY', investment='forex')

        self.position_set.manager.filled_orders = self.filled_orders
        self.position_set.save()

        print 'run update_fk...'
        ref = self.position_set.manager.update_foreign_keys()

        self.filled_orders = ref['filled_orders']
        self.position_forexs = ref['position_forexs']

        for position_forex in self.position_forexs:
            print position_forex
            print position_forex.position_set
            self.assertEqual(position_forex.position_set, self.position_set)


class TestPositionSetController(TestPositionSetCls):
    def setUp(self):
        TestPositionSetCls.setUp(self)

        self.controller = None
        self.filled_orders = None
        self.position_sets = list()

        # both open and close filled orders
        self.filled_orders = FilledOrder.objects.filter(
            Q(trade_summary__date__gte='2015-01-29')
            & Q(trade_summary__date__lt='2015-02-18')
            & Q(pos_effect='TO OPEN')
        )

        self.controller = PositionSetController(self.filled_orders)

    def tearDown(self):
        TestPositionSetCls.tearDown(self)

        # clean up
        """
        for position_set in self.position_sets:
            position_set.filledorder_set.update(position_set=None)
            position_set.positioninstrument_set.update(position_set=None)
            position_set.positionfuture_set.update(position_set=None)
            position_set.positionforex_set.update(position_set=None)
            position_set.profitloss_set.update(position_set=None)

            position_set.delete()

        #PositionSet.objects.all().delete()
        self.assertFalse(PositionSet.objects.count(), msg='Please reset db.')
        """

    def test_init_set_queries(self):
        """
        Test init set merge filter query
        """
        print 'output all queries...'
        for query in self.controller.queries:
            print '> %s' % query
            self.assertEqual(type(query), Q)

    def test_create_position_set(self):
        """
        Test create position_sets from filled_orders
        """
        print 'run create_position_sets'
        self.position_sets = self.controller.create_position_sets()
        self.assertEqual(type(self.position_sets), list)

        for position_set in self.position_sets:
            position_set = position_set
            """:type: PositionSet"""
            print '> id: %d - %s' % (position_set.id, position_set)

            self.assertEqual(type(position_set), PositionSet)

    def test_close_position_sets(self):
        """
        Test close position_sets using filled_orders
        """
        open_position_sets = self.controller.create_position_sets()

        # both open and close filled orders
        self.filled_orders = FilledOrder.objects.filter(
            Q(trade_summary__date__gt='2015-01-29')
            & Q(trade_summary__date__lt='2015-02-19')
            & Q(pos_effect='TO CLOSE')
        )

        self.controller = PositionSetController(self.filled_orders)

        self.position_sets = self.controller.close_position_sets()

        for position_set in self.position_sets:
            print position_set
            print 'id: %d' % position_set.id
            print 'status: %s' % position_set.status
            print '.' * 60

            self.assertEqual(type(position_set), PositionSet)
            self.assertEqual(position_set.status, 'CLOSE')

        # set back all open position_set
        self.position_sets = list()
        for position_set in open_position_sets:
            self.position_sets.append(
                PositionSet.objects.get(id=position_set.id)
            )

    def test_batch_update_foreign_keys(self):
        """
        Test update foreign keys when there was no filled orders
        """
        # only update one day foreign keys
        self.filled_orders = FilledOrder.objects.filter(
            Q(trade_summary__date='2015-01-29')
        )

        self.controller = PositionSetController(self.filled_orders)
        self.position_sets = self.controller.create_position_sets(date='2015-01-29')

        print 'run update_foreign_keys...\n\n'
        self.controller.batch_update_foreign_keys(date='2015-01-30')

        for position_set in self.position_sets:
            position_set = position_set
            """:type: PositionSet"""
            print position_set

            print position_set.filledorder_set.all()

            if position_set.underlying:
                print position_set.positioninstrument_set.all()
                print position_set.profitloss_set.all()
                self.assertEqual(position_set.positioninstrument_set.count(), 2)
                self.assertEqual(position_set.profitloss_set.count(), 2)
            elif position_set.future:
                print position_set.positionfuture_set.all()
                print position_set.profitloss_set.all()
                self.assertEqual(position_set.positionfuture_set.count(), 2)
                self.assertEqual(position_set.profitloss_set.count(), 2)
            elif position_set.forex:
                print position_set.positionforex_set.all()
                self.assertEqual(position_set.positionforex_set.count(), 2)

            print '.' * 60























