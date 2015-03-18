from position.classes.context.tests import *
from position.classes.context.spread.leg_two.vertical.vertical import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongCallVertical(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 80, 'price': 3.15, 'net_price': 0.0},
            'sell_call': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                          'strike': 85, 'price': 1.51, 'net_price': 4.66},
        }

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['buy_call']['contract'],
            side=self.orders['buy_call']['side'],
            quantity=self.orders['buy_call']['quantity'],
            strike=self.orders['buy_call']['strike'],
            price=self.orders['buy_call']['price'],
            net_price=self.orders['buy_call']['net_price']
        )

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['sell_call']['contract'],
            side=self.orders['sell_call']['side'],
            quantity=self.orders['sell_call']['quantity'],
            strike=self.orders['sell_call']['strike'],
            price=self.orders['sell_call']['price'],
            net_price=self.orders['sell_call']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100

        self.long_call_vertical = ContextLongCallVertical(
            filled_orders=filled_orders,
            contract_right=self.contract_right
        )
        contexts = self.long_call_vertical.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.buy_order.delete()
        self.sell_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), 81.64)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), 81.64)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), 81.64)
            self.assertEqual(start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side max profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(max_profit.price,
                             self.sell_order.strike)
            self.assertEqual(max_profit.condition, '>=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(float(max_profit.amount), 336.00)

    def test_max_loss(self):
        """
        Left side max profit
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(max_loss.price,
                             self.buy_order.strike)
            self.assertEqual(max_loss.condition, '<=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(float(max_loss.amount), -164.00)

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


class TestContextShortCallVertical(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 80, 'price': 3.15, 'net_price': 0.0},
            'sell_call': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                          'strike': 75, 'price': 5.6, 'net_price': -2.45},
        }

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['buy_call']['contract'],
            side=self.orders['buy_call']['side'],
            quantity=self.orders['buy_call']['quantity'],
            strike=self.orders['buy_call']['strike'],
            price=self.orders['buy_call']['price'],
            net_price=self.orders['buy_call']['net_price']
        )

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['sell_call']['contract'],
            side=self.orders['sell_call']['side'],
            quantity=self.orders['sell_call']['quantity'],
            strike=self.orders['sell_call']['strike'],
            price=self.orders['sell_call']['price'],
            net_price=self.orders['sell_call']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100

        self.short_call_vertical = ContextShortCallVertical(
            filled_orders=filled_orders,
            contract_right=self.contract_right
        )

        contexts = self.short_call_vertical.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.buy_order.delete()
        self.sell_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), 77.55)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), 77.55)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), 77.55)
            self.assertEqual(start_loss.condition, '>')

    def test_max_profit(self):
        """
        Left side max profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(max_profit.price,
                             self.sell_order.strike)
            self.assertEqual(max_profit.condition, '<=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(float(max_profit.amount), 245)

    def test_max_loss(self):
        """
        Left side max profit
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(max_loss.price,
                             self.buy_order.strike)
            self.assertEqual(max_loss.condition, '>=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(float(max_loss.amount), -255)

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


class TestContextLongPutVertical(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'buy_put': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                        'strike': 26, 'price': 1.2, 'net_price': 0.0},
            'sell_put': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                         'strike': 25, 'price': 0.65, 'net_price': 0.55},
        }

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['buy_put']['contract'],
            side=self.orders['buy_put']['side'],
            quantity=self.orders['buy_put']['quantity'],
            strike=self.orders['buy_put']['strike'],
            price=self.orders['buy_put']['price'],
            net_price=self.orders['buy_put']['net_price']
        )

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['sell_put']['contract'],
            side=self.orders['sell_put']['side'],
            quantity=self.orders['sell_put']['quantity'],
            strike=self.orders['sell_put']['strike'],
            price=self.orders['sell_put']['price'],
            net_price=self.orders['sell_put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100

        self.short_call_vertical = ContextLongPutVertical(
            filled_orders=filled_orders,
            contract_right=self.contract_right
        )

        contexts = self.short_call_vertical.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.buy_order.delete()
        self.sell_order.delete()

    def test_break_even(self):
        """
        Left side br eak even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), 25.45)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), 25.45)
            self.assertEqual(start_profit.condition, '<')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), 25.45)
            self.assertEqual(start_loss.condition, '>')

    def test_max_profit(self):
        """
        Left side max profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(max_profit.price,
                             self.sell_order.strike)
            self.assertEqual(max_profit.condition, '<=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(float(max_profit.amount), 45)

    def test_max_loss(self):
        """
        Left side max profit
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(max_loss.price,
                             self.buy_order.strike)
            self.assertEqual(max_loss.condition, '>=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(float(max_loss.amount), -55)

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


class TestContextShortPutVertical(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'buy_put': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                        'strike': 25, 'price': 0.65, 'net_price': 0.0},
            'sell_put': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                         'strike': 27, 'price': 1.91, 'net_price': -1.26},
        }

        self.buy_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['buy_put']['contract'],
            side=self.orders['buy_put']['side'],
            quantity=self.orders['buy_put']['quantity'],
            strike=self.orders['buy_put']['strike'],
            price=self.orders['buy_put']['price'],
            net_price=self.orders['buy_put']['net_price']
        )

        self.sell_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='VERTICAL',
            contract=self.orders['sell_put']['contract'],
            side=self.orders['sell_put']['side'],
            quantity=self.orders['sell_put']['quantity'],
            strike=self.orders['sell_put']['strike'],
            price=self.orders['sell_put']['price'],
            net_price=self.orders['sell_put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100

        self.short_call_vertical = ContextShortPutVertical(
            filled_orders=filled_orders,
            contract_right=self.contract_right
        )

        contexts = self.short_call_vertical.create_context()

        self.break_evens = contexts['break_evens']
        self.start_profits = contexts['start_profits']
        self.start_losses = contexts['start_losses']
        self.max_profits = contexts['max_profits']
        self.max_losses = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.buy_order.delete()
        self.sell_order.delete()

    def test_break_even(self):
        """
        Left side break even
        """
        for break_even in self.break_evens:
            print break_even
            self.assertFalse(break_even.id)
            self.assertEqual(float(break_even.price), 25.74)
            self.assertEqual(break_even.condition, '==')

    def test_start_profit(self):
        """
        Left side start profit
        """
        for start_profit in self.start_profits:
            print start_profit
            self.assertFalse(start_profit.id)
            self.assertEqual(float(start_profit.price), 25.74)
            self.assertEqual(start_profit.condition, '>')

    def test_start_loss(self):
        """
        Left side start loss
        """
        for start_loss in self.start_losses:
            print start_loss
            self.assertFalse(start_loss.id)
            self.assertEqual(float(start_loss.price), 25.74)
            self.assertEqual(start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side max profit
        """
        for max_profit in self.max_profits:
            print max_profit
            self.assertFalse(max_profit.id)
            self.assertEqual(max_profit.price,
                             self.sell_order.strike)
            self.assertEqual(max_profit.condition, '<=')
            self.assertTrue(max_profit.limit)
            self.assertEqual(float(max_profit.amount), 126)

    def test_max_loss(self):
        """
        Left side max profit
        """
        for max_loss in self.max_losses:
            print max_loss
            self.assertFalse(max_loss.id)
            self.assertEqual(max_loss.price,
                             self.buy_order.strike)
            self.assertEqual(max_loss.condition, '>=')
            self.assertTrue(max_loss.limit)
            self.assertEqual(float(max_loss.amount), -74)

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