from position.classes.context.tests import TestUnitSetUpDB
from position.classes.tests import create_filled_order
from position.classes.context.option.option import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongCall(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='CALL',
            side='BUY',
            quantity=2,
            strike=58,
            price=0.95
        )

        self.contract_right = 100
        self.price_multiply = 10

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.long_call = ContextLongCall(
            filled_orders=filled_orders
        )
        contexts = self.long_call.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.option_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price),
                             self.option_order.strike + self.option_order.price)
            self.assertEqual(float(break_even.price), 58.95)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price),
                             self.option_order.strike + self.option_order.price)
            self.assertEqual(float(start_profit.price), 58.95)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price),
                             self.option_order.strike + self.option_order.price)
            self.assertEqual(float(start_loss.price), 58.95)
            self.assertEqual(start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price),
                             self.option_order.strike + (self.option_order.price * self.price_multiply))
            self.assertEqual(max_profit.condition, '>=')
            self.assertFalse(max_profit.limit)
            self.assertEqual(float(max_profit.amount),
                             self.option_order.price * self.option_order.quantity
                             * self.price_multiply * self.contract_right)
            self.assertEqual(float(max_profit.amount), 1900.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price), self.option_order.strike)
            self.assertEqual(max_loss.condition, '<=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(max_loss.amount,
                             self.option_order.price * self.option_order.quantity
                             * self.contract_right * -1)
            self.assertEqual(float(max_loss.amount), -190.00)

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


class TestContextNakedCall(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='CALL',
            side='SELL',
            quantity=-4,
            strike=100,
            price=2.9
        )

        self.contract_right = 100
        self.price_multiply = 10

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.naked_call = ContextNakedCall(
            filled_orders=filled_orders
        )
        contexts = self.naked_call.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.option_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price),
                             self.option_order.strike + self.option_order.price)
            self.assertEqual(float(break_even.price), 102.9)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price),
                             self.option_order.strike + self.option_order.price)
            self.assertEqual(float(start_profit.price), 102.9)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price),
                             self.option_order.strike + self.option_order.price)
            self.assertEqual(float(start_loss.price), 102.9)
            self.assertEqual(start_loss.condition, '>')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price), self.option_order.strike)
            self.assertEqual(max_profit.condition, '<=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(float(max_profit.amount),
                             self.option_order.price * self.option_order.quantity
                             * self.contract_right * -1)
            self.assertEqual(float(max_profit.amount), 1160.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             self.option_order.strike + (self.option_order.price * self.price_multiply))
            self.assertEqual(max_loss.condition, '>=')
            self.assertFalse(max_loss.limit)
            self.assertEqual(float(max_loss.amount),
                             self.option_order.price * self.option_order.quantity
                             * self.price_multiply * self.contract_right)
            self.assertEqual(float(max_loss.amount), -11600.00)

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


class TestContextLongPut(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='BUY',
            quantity=5,
            strike=58,
            price=3.00
        )

        self.contract_right = 100
        self.price_multiply = 10

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.long_put = ContextLongPut(
            filled_orders=filled_orders
        )
        contexts = self.long_put.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.option_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price),
                             self.option_order.strike - self.option_order.price)
            self.assertEqual(float(break_even.price), 55.00)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price),
                             self.option_order.strike - self.option_order.price)
            self.assertEqual(float(start_profit.price), 55.00)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price),
                             self.option_order.strike - self.option_order.price)
            self.assertEqual(float(start_loss.price), 55.00)
            self.assertEqual(start_loss.condition, '>')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price),
                             self.option_order.strike - (self.option_order.price * self.price_multiply))
            self.assertEqual(float(max_profit.price), 28.00)
            self.assertEqual(max_profit.condition, '==')
            self.assertTrue(max_profit.limit)
            self.assertEqual(
                float(max_profit.amount),
                ((float(self.break_evens[0].price) -
                  (self.option_order.strike - (self.option_order.price * self.price_multiply)))
                 * self.option_order.quantity * self.contract_right)
            )
            self.assertEqual(float(max_profit.amount), 13500.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price), self.option_order.strike)
            self.assertEqual(max_loss.condition, '>=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(max_loss.amount,
                             self.option_order.price * self.option_order.quantity
                             * self.contract_right * -1)

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


class TestContextNakedPut(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='SELL',
            quantity=-9,
            strike=32,
            price=1.70
        )

        self.contract_right = 100
        self.price_multiply = 10

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.naked_put = ContextNakedPut(
            filled_orders=filled_orders
        )
        contexts = self.naked_put.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.option_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price),
                             self.option_order.strike - self.option_order.price)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price),
                             self.option_order.strike - self.option_order.price)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price),
                             self.option_order.strike - self.option_order.price)
            self.assertEqual(start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price), self.option_order.strike)
            self.assertEqual(max_profit.condition, '>=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(float(max_profit.amount), 1530.00)
            self.assertEqual(float(max_profit.amount),
                             (self.option_order.price * self.option_order.quantity
                              * self.contract_right * -1))

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price), 15.00)
            self.assertEqual(max_loss.condition, '<=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(max_loss.amount, -13770.00)
            self.assertEqual(
                max_loss.amount,
                round((float(self.break_evens[0].price) -
                       (self.option_order.strike - (self.option_order.price * self.price_multiply)))
                      * self.option_order.quantity * self.contract_right, 2)
            )

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