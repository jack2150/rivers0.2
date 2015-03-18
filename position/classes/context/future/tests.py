from position.classes.context.tests import TestUnitSetUpDB
from position.classes.tests import create_filled_order
from position.classes.context.future.future import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongFuture(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.future_order = create_filled_order(
            trade_summary=self.trade_summary,
            future=self.future,
            spread='FUTURE',
            contract='FUTURE',
            side='BUY',
            quantity=1,
            price=480.00,
            net_price=480.00
        )

        self.price_range = 0.2
        self.spc = float(Fraction(self.future.spc))

        filled_orders = FilledOrder.objects.filter(future=self.future).all()

        self.long_future = ContextLongFuture(
            filled_orders=filled_orders
        )
        contexts = self.long_future.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.future_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), self.future_order.price)
            self.assertEqual(float(break_even.price), 480.00)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), self.future_order.price)
            self.assertEqual(float(start_profit.price), 480.00)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), self.future_order.price)
            self.assertEqual(float(start_loss.price), 480.00)
            self.assertEqual(start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price),
                             self.future_order.price * (1 + self.price_range))
            self.assertEqual(max_profit.condition, '==')
            self.assertFalse(max_profit.limit)
            self.assertEqual(
                float(max_profit.amount),
                float(self.future_order.price * self.price_range) / self.spc
            )
            self.assertEqual(round(max_profit.amount, 2), 4800.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             self.future_order.price * (1 - self.price_range))
            self.assertEqual(max_loss.condition, '==')
            self.assertTrue(max_loss.limit)
            self.assertEqual(
                float(max_loss.amount),
                float(self.future_order.price * self.price_range) / -self.spc
            )
            self.assertEqual(round(max_loss.amount, 2), -4800.00)

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


class TestContextShortFuture(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.future_order = create_filled_order(
            trade_summary=self.trade_summary,
            future=self.future,
            spread='FUTURE',
            contract='FUTURE',
            side='SELL',
            quantity=-1,
            price=484.25,
            net_price=484.25
        )

        self.price_range = 0.2
        self.spc = float(Fraction(self.future.spc))

        filled_orders = FilledOrder.objects.filter(future=self.future).all()

        self.short_future = ContextShortFuture(
            filled_orders=filled_orders
        )
        contexts = self.short_future.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']
        
        self.spc = float(Fraction(self.future.spc))

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.future_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), self.future_order.price)
            self.assertEqual(float(break_even.price), 484.25)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), self.future_order.price)
            self.assertEqual(float(start_profit.price), 484.25)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), self.future_order.price)
            self.assertEqual(float(start_loss.price), 484.25)
            self.assertEqual(start_loss.condition, '>')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(round(max_profit.price, 2),
                             round(self.future_order.price * (1 - self.price_range), 2))
            self.assertEqual(max_profit.condition, '==')
            self.assertTrue(max_profit.limit)
            self.assertEqual(
                float(max_profit.amount),
                (
                    (self.future_order.price * self.price_range
                     * self.future_order.quantity) / -self.spc
                )
            )
            self.assertEqual(round(max_profit.amount, 2), 4842.5)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             self.future_order.price * (1 + self.price_range))
            self.assertEqual(max_loss.condition, '==')
            self.assertFalse(max_loss.limit)
            self.assertEqual(
                float(max_loss.amount),
                (
                    (self.future_order.price * self.price_range
                     * self.future_order.quantity) / self.spc
                )
            )
            self.assertEqual(round(max_loss.amount, 2), -4842.5)

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
