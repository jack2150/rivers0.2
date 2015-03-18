from position.classes.context.tests import TestUnitSetUpDB
from position.classes.tests import create_filled_order
from position.classes.context.hedge.hedge import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextCoveredCall(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)
        """
        Test create context data using filled orders
        """
        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'BUY', 'quantity': +100,
                      'strike': 0, 'price': 85.5, 'net_price': 0.0},
            'option': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1,
                       'strike': 85, 'price': 2.2, 'net_price': 83.3},
        }

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['stock']['contract'],
            side=self.orders['stock']['side'],
            quantity=self.orders['stock']['quantity'],
            strike=self.orders['stock']['strike'],
            price=self.orders['stock']['price'],
            net_price=self.orders['stock']['net_price']
        )

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['option']['contract'],
            side=self.orders['option']['side'],
            quantity=self.orders['option']['quantity'],
            strike=self.orders['option']['strike'],
            price=self.orders['option']['price'],
            net_price=self.orders['option']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.price_range = 0.2

        self.covered_call = ContextCoveredCall(
            filled_orders=filled_orders
        )

        contexts = self.covered_call.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()
        self.option_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price),
                             self.stock_order.price - self.option_order.price)
            self.assertEqual(float(break_even.price), 83.3)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price),
                             self.stock_order.price - self.option_order.price)
            self.assertEqual(float(start_profit.price), 83.3)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price),
                             self.stock_order.price - self.option_order.price)
            self.assertEqual(float(start_loss.price), 83.3)
            self.assertEqual(start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price),
                             self.option_order.strike)
            self.assertEqual(max_profit.condition, '>=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(
                float(max_profit.amount),
                float(round((self.option_order.strike - self.stock_order.price
                             + self.option_order.price) * self.stock_order.quantity, 2))
            )
            self.assertEqual(float(max_profit.amount), 170.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price), 68.4)
            self.assertEqual(max_loss.condition, '<=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(
                round(max_loss.amount, 2),
                round(
                    (float(self.break_evens[0].price)
                     - (self.stock_order.price * (1 - self.price_range)))
                    * self.stock_order.quantity * -1, 2
                )
            )
            self.assertEqual(round(max_loss.amount, 2), -1490.00)

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


class TestContextProtectiveCall(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)
        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'SELL', 'quantity': +100,
                      'strike': 0, 'price': 85.5, 'net_price': 0.0},
            'option': {'contract': 'CALL', 'side': 'BUY', 'quantity': -1,
                       'strike': 85, 'price': 2.2, 'net_price': 82.93},
        }

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['stock']['contract'],
            side=self.orders['stock']['side'],
            quantity=self.orders['stock']['quantity'],
            strike=self.orders['stock']['strike'],
            price=self.orders['stock']['price'],
            net_price=self.orders['stock']['net_price']
        )

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['option']['contract'],
            side=self.orders['option']['side'],
            quantity=self.orders['option']['quantity'],
            strike=self.orders['option']['strike'],
            price=self.orders['option']['price'],
            net_price=self.orders['option']['net_price']
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.protective_call = ContextProtectiveCall(
            filled_orders=filled_orders
        )
        contexts = self.protective_call.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()
        self.option_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price),
                             self.stock_order.price - self.option_order.price)
            self.assertEqual(break_even.condition, '==')
            print break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price),
                             self.stock_order.price - self.option_order.price)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price),
                             self.stock_order.price - self.option_order.price)
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
            self.assertEqual(float(max_profit.price), 68.4)
            self.assertEqual(max_profit.condition, '<=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(
                round(max_profit.amount, 2),
                round(
                    (float(self.break_evens[0].price) -
                     (self.stock_order.price * (1 - self.price_range)))
                    * self.stock_order.quantity, 2
                )
            )
            self.assertEqual(round(max_profit.amount, 2), 1490.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price), self.option_order.strike)
            self.assertEqual(float(max_loss.price), 85.0)
            self.assertEqual(max_loss.condition, '>=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(
                round(max_loss.amount, 2),
                round(
                    (self.option_order.strike - self.stock_order.price + self.option_order.price)
                    * self.stock_order.quantity * -1, 2
                )
            )
            self.assertEqual(float(max_loss.amount), -170.00)

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


class TestContextCoveredPut(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'SELL', 'quantity': -100,
                      'strike': 0, 'price': 85.5, 'net_price': 0.0},
            'option': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                       'strike': 85, 'price': 2.2, 'net_price': 82.93},
        }

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['stock']['contract'],
            side=self.orders['stock']['side'],
            quantity=self.orders['stock']['quantity'],
            strike=self.orders['stock']['strike'],
            price=self.orders['stock']['price'],
            net_price=self.orders['stock']['net_price']
        )

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['option']['contract'],
            side=self.orders['option']['side'],
            quantity=self.orders['option']['quantity'],
            strike=self.orders['option']['strike'],
            price=self.orders['option']['price'],
            net_price=self.orders['option']['net_price']
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.covered_call = ContextCoveredPut(
            filled_orders=filled_orders
        )
        contexts = self.covered_call.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()
        self.option_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price),
                             self.stock_order.price + self.option_order.price)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price),
                             self.stock_order.price + self.option_order.price)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price),
                             self.stock_order.price + self.option_order.price)
            self.assertEqual(start_loss.condition, '>')

    def test_max_profit(self):
        """
        Left side start profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(float(max_profit.price),
                             self.option_order.strike)
            self.assertEqual(max_profit.condition, '<=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(
                float(max_profit.amount),
                float(round((self.option_order.strike - self.stock_order.price - self.option_order.price)
                            * self.stock_order.quantity))
            )
            self.assertEqual(round(max_profit.amount, 2), 270.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             self.stock_order.price * (1 + self.price_range))
            self.assertEqual(max_loss.condition, '>=')
            self.assertFalse(max_loss.limit)
            self.assertEqual(
                round(max_loss.amount, 2),
                round(
                    (float(self.break_evens[0].price) -
                     (self.stock_order.price * (1 + self.price_range)))
                    * self.stock_order.quantity * -1, 2
                )
            )
            self.assertEqual(round(max_loss.amount, 2), -1490.00)

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


class TestContextProtectivePut(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'stock': {'contract': 'STOCK', 'side': 'SELL', 'quantity': -100,
                      'strike': 0, 'price': 85.5, 'net_price': 0.0},
            'option': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                       'strike': 85, 'price': 2.2, 'net_price': 82.93},
        }

        self.stock_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['stock']['contract'],
            side=self.orders['stock']['side'],
            quantity=self.orders['stock']['quantity'],
            strike=self.orders['stock']['strike'],
            price=self.orders['stock']['price'],
            net_price=self.orders['stock']['net_price']
        )

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COVERED',
            contract=self.orders['option']['contract'],
            side=self.orders['option']['side'],
            quantity=self.orders['option']['quantity'],
            strike=self.orders['option']['strike'],
            price=self.orders['option']['price'],
            net_price=self.orders['option']['net_price']
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.protective_put = ContextProtectivePut(
            filled_orders=filled_orders
        )
        contexts = self.protective_put.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()
        self.option_order.delete()
        
    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price),
                             self.stock_order.price + self.option_order.price)
            self.assertEqual(float(break_even.price), 87.7)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price),
                             self.stock_order.price + self.option_order.price)
            self.assertEqual(float(start_profit.price), 87.7)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price),
                             self.stock_order.price + self.option_order.price)
            self.assertEqual(float(start_loss.price), 87.7)
            self.assertEqual(start_loss.condition, '<')

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
                round(max_profit.amount, 2),
                round(
                    ((self.stock_order.price * (1 - self.price_range)) -
                     float(self.break_evens[0].price))
                    * self.stock_order.quantity, 2
                )
            )
            self.assertEqual(round(max_profit.amount, 2), 1930.00)

    def test_max_loss(self):
        """
        Left side max loss
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(float(max_loss.price),
                             self.option_order.strike)
            self.assertEqual(max_loss.condition, '>=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(
                float(max_loss.amount),
                float(round((self.option_order.strike - self.stock_order.price - self.option_order.price)
                            * self.stock_order.quantity * -1))
            )
            self.assertEqual(round(max_loss.amount, 2), -270.00)

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
