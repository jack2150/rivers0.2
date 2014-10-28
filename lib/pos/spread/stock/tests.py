from lib.test import TestReadyUp
from pms_app.pos_app.models import Underlying, PositionSet
import lib.pos.spread.stock as stock


class TestStockContext(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)

        self.ready_all(key=1)
        position = Underlying.objects.first()
        pos_set = PositionSet(position)

        self.stock_context = stock.StockContext(pos_set)

        self.set_prices = [12.5, 20.7, 33.94, 8.71, 114.81]
        self.set_conditions = ['>', '<', '==', '<=', '>=']
        self.test_prices = [13.9, 22.67, 33.94, 7.66, 100.88]

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.stock_context.json()[:80] + '...\n'

        self.assertTrue(eval(self.stock_context.json()))
        self.assertEqual(type(self.stock_context.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.stock_context.__unicode__()[:80] + '...\n'

        self.assertEqual(type(self.stock_context.__unicode__()), str)
        self.assertIn('Position', self.stock_context.__unicode__())

    def test_property(self):
        """
        Test all property inside class
        """
        # check models data exist
        print 'position id: %d' % self.stock_context.pos_set.instrument.id
        print 'instrument id: %d' % self.stock_context.pos_set.position.id
        print 'stock id: %d' % self.stock_context.pos_set.stock.id

        # check models data exist
        self.assertTrue(self.stock_context.pos_set.stock.id)
        self.assertTrue(self.stock_context.pos_set.stock.id)
        self.assertTrue(self.stock_context.pos_set.instrument.id)
        self.assertFalse(self.stock_context.pos_set.options.count())

    def test_is_profit(self):
        """
        Test is profit method
        """
        expect_results = [True, False, True, True, False]
        zipped = zip(self.set_prices, self.set_conditions, self.test_prices, expect_results)
        for set_price, condition, test_price, expect_result in zipped:
            self.stock_context.pl.start_profit.price = set_price
            self.stock_context.pl.start_profit.condition = condition

            result = self.stock_context.is_profit(test_price)

            print 'price: %.2f, condition: %s' % (set_price, condition)
            print 'test: %.2f, result: %s\n' % (test_price, result)

            self.assertEqual(result, expect_result)
            self.assertEqual(type(result), bool)

    def test_is_loss(self):
        """
        Test is loss method
        """
        expect_results = [True, False, True, True, False]
        zipped = zip(self.set_prices, self.set_conditions, self.test_prices, expect_results)
        for set_price, condition, test_price, expect_result in zipped:
            self.stock_context.pl.start_loss.price = set_price
            self.stock_context.pl.start_loss.condition = condition

            result = self.stock_context.is_loss(test_price)

            print 'price: %.2f, condition: %s' % (set_price, condition)
            print 'test: %.2f, result: %s\n' % (test_price, result)

            self.assertEqual(result, expect_result)
            self.assertEqual(type(result), bool)

    def test_is_even(self):
        """
        Test is even method
        """
        expect_results = [False, False, True, False, False]
        zipped = zip(self.set_prices, self.set_conditions, self.test_prices, expect_results)
        for set_price, _, test_price, expect_result in zipped:
            self.stock_context.pl.break_even.price = set_price
            self.stock_context.pl.break_even.condition = '=='

            result = self.stock_context.is_even(test_price)

            print 'price: %.2f, condition: %s' % (set_price, '==')
            print 'test: %.2f, result: %s\n' % (test_price, result)

            self.assertEqual(result, expect_result)
            self.assertEqual(type(result), bool)

    def test_update_status(self):
        """
        Test set status int
        """
        attrs = ['is_even', 'is_profit', 'is_loss']

        for attr in attrs:
            # set method into return true
            setattr(self.stock_context, attr, lambda price: True)

            status = self.stock_context.status

            print 'attr: %s, status: %s' % (attr, status)

            # test status in list
            self.assertIn(status, ['even', 'profit', 'loss'])

            # set method into return false
            setattr(self.stock_context, attr, lambda price: False)


class TestStockLong(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=1)

        position = Underlying.objects.first()
        self.pos_set = PositionSet(position)

        print 'Symbol: %s\n' % self.pos_set.stock.underlying.symbol

        self.stock_long = stock.StockLong(self.pos_set)

    def test_property(self):
        """
        Test stock short spread got correct property
        """
        print 'long stock property...'
        print 'name: %s, context: %s' % (
            self.stock_long.name,
            self.stock_long.context
        )

        self.assertEqual(self.stock_long.context, 'stock')
        self.assertEqual(self.stock_long.name, 'long_stock')

    def test_start_profit(self):
        """
        Test start profit in short stock spread
        """
        print 'start profit...'
        print 'price: %.2f, condition: %s' % (
            self.stock_long.pl.start_profit.price,
            self.stock_long.pl.start_profit.condition
        )

        self.assertEqual(self.stock_long.pl.start_profit.price,
                         self.stock_long.pl.break_even.price)
        self.assertEqual(self.stock_long.pl.start_profit.condition,
                         '>')

    def test_max_profit(self):
        """
        Test max profit in short stock spread
        """
        print 'max profit...'
        print 'loss: %.2f, limit: %s, price: %.2f, condition: %s' % (
            self.stock_long.pl.max_profit.amount,
            self.stock_long.pl.max_profit.limit,
            self.stock_long.pl.max_profit.price,
            self.stock_long.pl.max_profit.condition
        )

        self.assertEqual(self.stock_long.pl.max_profit.amount, 0)
        self.assertEqual(self.stock_long.pl.max_profit.limit, False)
        self.assertEqual(self.stock_long.pl.max_profit.price, float('inf'))
        self.assertEqual(self.stock_long.pl.max_profit.condition, '==')

    def test_start_loss(self):
        """
        Test start loss in short stock
        """
        print 'start loss...'
        print 'price: %.2f, condition: %s' % (
            self.stock_long.pl.start_loss.price,
            self.stock_long.pl.start_loss.condition
        )

        self.assertEqual(self.stock_long.pl.start_loss.price,
                         self.stock_long.pl.break_even.price)
        self.assertEqual(self.stock_long.pl.start_loss.condition,
                         '<')

    def test_max_loss(self):
        """
        Test max loss in short stock
        """
        print 'max loss...'
        print 'loss: %.2f, limit: %s, price: %.2f, condition: %s' % (
            self.stock_long.pl.max_loss.amount,
            self.stock_long.pl.max_loss.limit,
            self.stock_long.pl.max_loss.price,
            self.stock_long.pl.max_loss.condition
        )

        self.assertEqual(self.stock_long.pl.max_loss.amount,
                         float(self.pos_set.stock.trade_price * abs(self.pos_set.stock.quantity)))
        self.assertEqual(self.stock_long.pl.max_loss.limit, True)
        self.assertLess(self.stock_long.pl.max_loss.price, self.stock_long.pl.break_even.price)
        self.assertEqual(self.stock_long.pl.max_loss.condition, '==')

    def test_break_even(self):
        """
        Test break even in short stock
        """
        print 'break even...'
        print 'price: %.2f, condition: %s' % (
            self.stock_long.pl.break_even.price,
            self.stock_long.pl.break_even.condition
        )

        self.assertEqual(self.stock_long.pl.break_even.price,
                         float(self.pos_set.stock.trade_price))
        self.assertEqual(self.stock_long.pl.break_even.condition, '==')


class TestStockShort(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=1)

        position = Underlying.objects.first()
        self.pos_set = PositionSet(position)

        print 'Symbol: %s\n' % self.pos_set.stock.underlying.symbol

        self.stock_short = stock.StockShort(self.pos_set)

    def test_property(self):
        """
        Test stock short spread got correct property
        """
        print 'short stock property...'
        print 'name: %s, context: %s' % (
            self.stock_short.name,
            self.stock_short.context
        )

        self.assertEqual(self.stock_short.context, 'stock')
        self.assertEqual(self.stock_short.name, 'short_stock')

    def test_start_profit(self):
        """
        Test start profit in short stock spread
        """
        print 'start profit...'
        print 'price: %.2f, condition: %s' % (
            self.stock_short.pl.start_profit.price,
            self.stock_short.pl.start_profit.condition
        )

        self.assertEqual(self.stock_short.pl.start_profit.price,
                         self.stock_short.pl.break_even.price)
        self.assertEqual(self.stock_short.pl.start_profit.condition,
                         '<')

    def test_max_profit(self):
        """
        Test max profit in short stock spread
        """
        print 'max profit...'
        print 'loss: %.2f, limit: %s, price: %.2f, condition: %s' % (
            self.stock_short.pl.max_profit.amount,
            self.stock_short.pl.max_profit.limit,
            self.stock_short.pl.max_profit.price,
            self.stock_short.pl.max_profit.condition
        )

        self.assertEqual(self.stock_short.pl.max_profit.amount,
                         float(self.pos_set.stock.trade_price * abs(self.pos_set.stock.quantity)))
        self.assertEqual(self.stock_short.pl.max_profit.limit, True)
        self.assertLess(self.stock_short.pl.max_profit.price, self.stock_short.pl.break_even.price)
        self.assertEqual(self.stock_short.pl.max_profit.condition, '==')

    def test_start_loss(self):
        """
        Test start loss in short stock
        """
        print 'start loss...'
        print 'price: %.2f, condition: %s' % (
            self.stock_short.pl.start_loss.price,
            self.stock_short.pl.start_loss.condition
        )

        self.assertEqual(self.stock_short.pl.start_loss.price,
                         self.stock_short.pl.break_even.price)
        self.assertEqual(self.stock_short.pl.start_loss.condition, '>')

    def test_max_loss(self):
        """
        Test max loss in short stock
        """
        print 'max loss...'
        print 'loss: %.2f, limit: %s, price: %.2f, condition: %s' % (
            self.stock_short.pl.max_loss.amount,
            self.stock_short.pl.max_loss.limit,
            self.stock_short.pl.max_loss.price,
            self.stock_short.pl.max_loss.condition
        )

        self.assertEqual(self.stock_short.pl.max_loss.amount, float('inf'))
        self.assertEqual(self.stock_short.pl.max_loss.limit, False)
        self.assertGreater(self.stock_short.pl.max_loss.price,
                           self.stock_short.pl.break_even.price)
        self.assertEqual(self.stock_short.pl.max_loss.condition, '==')

    def test_break_even(self):
        """
        Test break even in short stock
        """
        print 'break even...'
        print 'price: %.2f, condition: %s' % (
            self.stock_short.pl.break_even.price,
            self.stock_short.pl.break_even.condition
        )

        self.assertEqual(self.stock_short.pl.break_even.price,
                         float(self.pos_set.stock.trade_price))
        self.assertEqual(self.stock_short.pl.break_even.condition, '==')