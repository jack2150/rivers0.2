from position.classes.context.tests import TestUnitSetUpDB
from position.classes.tests import create_filled_order
from position.classes.context.forex.forex import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongForex(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.forex_order = create_filled_order(
            trade_summary=self.trade_summary,
            forex=self.forex,
            spread='FOREX',
            contract='FOREX',
            side='BUY',
            quantity=10000,
            price=120.1295
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(forex=self.forex).all()

        self.long_forex = ContextLongForex(
            filled_orders=filled_orders
        )
        contexts = self.long_forex.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.forex_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), self.forex_order.price)
            self.assertEqual(float(break_even.price), 120.1295)
            self.assertEqual(break_even.condition, '==')
            print break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), self.forex_order.price)
            self.assertEqual(float(start_profit.price), 120.1295)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), self.forex_order.price)
            self.assertEqual(float(start_loss.price), 120.1295)
            self.assertEqual(start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price),
                             round(self.forex_order.price * (1 + self.price_range), 6))
            self.assertEqual(max_profit.condition, '>=')
            self.assertFalse(max_profit.limit)
            self.assertEqual(
                float(round(max_profit.amount, 2)),
                round(((self.forex_order.price * (1 + self.price_range) * self.forex_order.quantity)
                       - (self.forex_order.price * self.forex_order.quantity))
                      / (self.forex_order.price * (1 + self.price_range)), 2)
            )
            self.assertEqual(round(max_profit.amount, 2), 1666.67)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             self.forex_order.price * (1 - self.price_range))
            self.assertEqual(max_loss.condition, '<=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(
                round(max_loss.amount, 2),
                round(
                    ((self.forex_order.price * (1 - self.price_range) * self.forex_order.quantity)
                     - (self.forex_order.price * self.forex_order.quantity))
                    / (self.forex_order.price * (1 - self.price_range)), 2
                )
            )
            self.assertEqual(round(max_loss.amount, 2), -2500.00)

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


class TestContextShortForex(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.forex_order = create_filled_order(
            trade_summary=self.trade_summary,
            forex=self.forex,
            spread='FOREX',
            contract='FOREX',
            side='SELL',
            quantity=-10000,
            price=120.1295
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(forex=self.forex).all()

        self.short_forex = ContextShortForex(
            filled_orders=filled_orders
        )
        contexts = self.short_forex.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.forex_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), self.forex_order.price)
            self.assertEqual(float(break_even.price), 120.1295)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), self.forex_order.price)
            self.assertEqual(float(start_profit.price), 120.1295)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), self.forex_order.price)
            self.assertEqual(float(start_loss.price), 120.1295)
            self.assertEqual(start_loss.condition, '>')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price),
                             self.forex_order.price * (1 - self.price_range))
            self.assertEqual(max_profit.condition, '<=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(
                round(max_profit.amount, 2),
                round(
                    ((self.forex_order.price * (1 - self.price_range) * self.forex_order.quantity)
                     - (self.forex_order.price * self.forex_order.quantity))
                    / (self.forex_order.price * (1 - self.price_range)), 2
                )
            )
            self.assertEqual(round(max_profit.amount, 2), 2500.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             round(self.forex_order.price * (1 + self.price_range), 6))
            self.assertEqual(max_loss.condition, '>=')
            self.assertFalse(max_loss.limit)
            self.assertEqual(
                float(round(max_loss.amount, 2)),
                round(((self.forex_order.price * (1 + self.price_range) * self.forex_order.quantity)
                       - (self.forex_order.price * self.forex_order.quantity))
                      / (self.forex_order.price * (1 + self.price_range)), 2)
            )
            self.assertEqual(round(max_loss.amount, 2), -1666.67)

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