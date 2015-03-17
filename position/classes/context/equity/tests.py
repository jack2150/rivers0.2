from position.classes.context.tests import TestUnitSetUpDB
from position.classes.tests import create_filled_order
from position.classes.context.equity.equity import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongStock(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STOCK',
            contract='ETF',
            side='BUY',
            quantity=10,
            price=374.24
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.long_stock = ContextLongStock(
            filled_orders=filled_orders
        )
        self.position_context = self.long_stock.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()

    def test_position_context(self):
        """
        Position context
        """
        self.assertTrue(self.position_context.id)
        print self.position_context

    def test_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_context.break_even.id)
        self.assertEqual(float(self.position_context.break_even.price), self.stock_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 374.24)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), self.stock_order.price)
        self.assertEqual(float(self.position_context.start_profit.price), 374.24)
        self.assertEqual(self.position_context.start_profit.condition, '>')

        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), self.stock_order.price)
        self.assertEqual(float(self.position_context.start_loss.price), 374.24)
        self.assertEqual(self.position_context.start_loss.condition, '<')

        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(round(self.position_context.max_profit.price, 2),
                         round(self.stock_order.price * (1 + self.price_range), 2))
        self.assertEqual(round(self.position_context.max_profit.price, 2), 449.09)
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            self.stock_order.price * self.price_range * self.stock_order.quantity
        )
        self.assertEqual(float(self.position_context.max_profit.amount), 748.48)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         self.stock_order.price * (1 - self.price_range))
        self.assertEqual(round(self.position_context.max_loss.price, 2), 299.39)
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            (self.stock_order.price * self.price_range)
            * self.stock_order.quantity * -1
        )
        self.assertEqual(float(self.position_context.max_loss.amount), -748.48)
        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss


class TestContextShortStock(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STOCK',
            contract='ETF',
            side='SELL',
            quantity=-100,
            price=16.5
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.short_stock = ContextShortStock(
            filled_orders=filled_orders
        )
        self.position_context = self.short_stock.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()

    def test_position_context(self):
        """
        Position context
        """
        self.assertTrue(self.position_context.id)
        print self.position_context

    def test_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_context.break_even.id)
        self.assertEqual(float(self.position_context.break_even.price), self.stock_order.price)
        self.assertEqual(self.position_context.break_even.price, 16.5)
        self.assertEqual(self.position_context.break_even.condition, '==')

        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), self.stock_order.price)
        self.assertEqual(self.position_context.start_profit.price, 16.5)
        self.assertEqual(self.position_context.start_profit.condition, '<')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), self.stock_order.price)
        self.assertEqual(self.position_context.start_loss.price, 16.5)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         self.stock_order.price * (1 - self.price_range))
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            self.stock_order.price * self.price_range * self.stock_order.quantity * -1
        )
        self.assertEqual(float(self.position_context.max_profit.amount), 330.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         self.stock_order.price * (1 + self.price_range))
        self.assertEqual(float(self.position_context.max_loss.price), 19.80)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            (self.stock_order.price * self.price_range)
            * self.stock_order.quantity
        )
        self.assertEqual(float(self.position_context.max_loss.amount), -330.00)
        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss