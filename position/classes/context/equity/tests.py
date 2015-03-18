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

        contexts = self.long_stock.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), self.stock_order.price)
            self.assertEqual(float(break_even.price), 374.24)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), self.stock_order.price)
            self.assertEqual(float(start_profit.price), 374.24)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), self.stock_order.price)
            self.assertEqual(float(start_loss.price), 374.24)
            self.assertEqual(start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(round(max_profit.price, 2),
                             round(self.stock_order.price * (1 + self.price_range), 2))
            self.assertEqual(round(max_profit.price, 2), 449.09)
            self.assertEqual(max_profit.condition, '>=')
            self.assertFalse(max_profit.limit)
            self.assertEqual(
                float(max_profit.amount),
                self.stock_order.price * self.price_range * self.stock_order.quantity
            )
            self.assertEqual(float(max_profit.amount), 748.48)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             self.stock_order.price * (1 - self.price_range))
            self.assertEqual(round(max_loss.price, 2), 299.39)
            self.assertEqual(max_loss.condition, '<=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(
                float(max_loss.amount),
                (self.stock_order.price * self.price_range)
                * self.stock_order.quantity * -1
            )
            self.assertEqual(float(max_loss.amount), -748.48)

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.break_evens
        print self.start_profits
        print self.start_losses
        print self.max_profits
        print self.max_losses


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
        contexts = self.short_stock.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), self.stock_order.price)
            self.assertEqual(break_even.price, 16.5)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), self.stock_order.price)
            self.assertEqual(start_profit.price, 16.5)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), self.stock_order.price)
            self.assertEqual(start_loss.price, 16.5)
            self.assertEqual(start_loss.condition, '>')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price),
                             self.stock_order.price * (1 - self.price_range))
            self.assertEqual(max_profit.condition, '<=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(
                float(max_profit.amount),
                self.stock_order.price * self.price_range * self.stock_order.quantity * -1
            )
            self.assertEqual(float(max_profit.amount), 330.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             self.stock_order.price * (1 + self.price_range))
            self.assertEqual(float(max_loss.price), 19.80)
            self.assertEqual(max_loss.condition, '>=')
            self.assertFalse(max_loss.limit)
            self.assertEqual(
                float(max_loss.amount),
                (self.stock_order.price * self.price_range)
                * self.stock_order.quantity
            )
            self.assertEqual(float(max_loss.amount), -330.00)

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.break_evens
        print self.start_profits
        print self.start_losses
        print self.max_profits
        print self.max_losses