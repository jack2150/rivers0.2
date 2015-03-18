from position.classes.context.tests import *
from position.classes.context.spread.leg_two.combo.combo import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongCombo(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'buy_call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                         'strike': 55, 'price': 1.0, 'net_price': 0.0},
            'sell_put': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                         'strike': 49, 'price': 1.1, 'net_price': -0.1},
        }

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract=self.orders['buy_call']['contract'],
            side=self.orders['buy_call']['side'],
            quantity=self.orders['buy_call']['quantity'],
            strike=self.orders['buy_call']['strike'],
            price=self.orders['buy_call']['price'],
            net_price=self.orders['buy_call']['net_price']
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract=self.orders['sell_put']['contract'],
            side=self.orders['sell_put']['side'],
            quantity=self.orders['sell_put']['quantity'],
            strike=self.orders['sell_put']['strike'],
            price=self.orders['sell_put']['price'],
            net_price=self.orders['sell_put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100
        self.price_range = 0.2

        self.long_combo = ContextLongCombo(
            filled_orders=filled_orders,
            contract_right=self.contract_right
        )
        contexts = self.long_combo.create_context()

        self.left_break_even, self.right_break_even = contexts['break_evens']
        self.left_start_profit, self.right_start_profit = contexts['start_profits']
        self.left_start_loss, self.right_start_loss = contexts['start_losses']
        self.left_max_profit, self.right_max_profit = contexts['max_profits']
        self.left_max_loss, self.right_max_loss = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.call_order.delete()
        self.put_order.delete()

    def test_left_break_even(self):
        """
        Left side break even
        """
        print self.left_break_even
        self.assertFalse(self.left_break_even.id)
        self.assertEqual(float(self.left_break_even.price), self.put_order.strike)
        self.assertEqual(self.left_break_even.condition, '>=')
        self.assertEqual(float(self.left_break_even.amount), 10.00)

    def test_left_start_loss(self):
        """
        Left side start loss
        """
        print self.left_start_loss
        self.assertFalse(self.left_start_loss.id)
        self.assertEqual(float(self.left_start_loss.price),
                         self.put_order.strike)
        self.assertEqual(self.left_start_loss.condition, '<')

    def test_left_max_loss(self):
        """
        Left side max loss
        """
        print self.left_max_loss
        self.assertFalse(self.left_max_loss.id)
        self.assertEqual(float(self.left_max_loss.price),
                         self.put_order.strike * (1 - self.price_range))
        self.assertEqual(self.left_max_loss.condition, '<=')
        self.assertTrue(self.left_max_loss.limit)
        self.assertEqual(float(self.left_max_loss.amount), -970.00)

    def test_right_break_even(self):
        """
        Right break even
        """
        print self.right_break_even
        self.assertFalse(self.right_break_even.id)
        self.assertEqual(float(self.right_break_even.price), self.call_order.strike)
        self.assertEqual(self.right_break_even.condition, '<=')
        self.assertEqual(self.right_break_even.amount, 10.00)

    def test_right_start_profit(self):
        """
        Right start profit
        """
        print self.right_start_profit
        self.assertFalse(self.right_start_profit.id)
        self.assertEqual(float(self.right_start_profit.price), self.call_order.strike)
        self.assertEqual(self.right_start_profit.condition, '>')

    def test_right_max_profit(self):
        """
        Right max profit
        """
        print self.right_max_profit
        self.assertFalse(self.right_max_profit.id)
        self.assertEqual(self.right_max_profit.price,
                         self.right_break_even.price * Decimal(1 + self.price_range))
        self.assertEqual(self.right_max_profit.condition, '>=')
        self.assertFalse(self.right_max_profit.limit)
        self.assertEqual(self.right_max_profit.amount, 1110.00)

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print '.' * 60
        print self.left_break_even, self.right_break_even
        print self.left_start_profit, self.right_start_profit
        print self.left_start_loss, self.right_start_loss
        print self.left_max_profit, self.right_max_profit
        print self.left_max_loss, self.right_max_loss


class TestContextShortCombo(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'buy_put': {'contract': 'PUT', 'side': 'BUY', 'quantity': +1,
                        'strike': 540, 'price': 16.2, 'net_price': 0.0},
            'sell_call': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1,
                          'strike': 570, 'price': 12.8, 'net_price': 3.4},
        }

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract=self.orders['buy_put']['contract'],
            side=self.orders['buy_put']['side'],
            quantity=self.orders['buy_put']['quantity'],
            strike=self.orders['buy_put']['strike'],
            price=self.orders['buy_put']['price'],
            net_price=self.orders['buy_put']['net_price']
        )

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='COMBO',
            contract=self.orders['sell_call']['contract'],
            side=self.orders['sell_call']['side'],
            quantity=self.orders['sell_call']['quantity'],
            strike=self.orders['sell_call']['strike'],
            price=self.orders['sell_call']['price'],
            net_price=self.orders['sell_call']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100
        self.price_range = 0.2

        self.long_combo = ContextShortCombo(
            filled_orders=filled_orders,
            contract_right=self.contract_right
        )
        contexts = self.long_combo.create_context()

        self.left_break_even, self.right_break_even = contexts['break_evens']
        self.left_start_profit, self.right_start_profit = contexts['start_profits']
        self.left_start_loss, self.right_start_loss = contexts['start_losses']
        self.left_max_profit, self.right_max_profit = contexts['max_profits']
        self.left_max_loss, self.right_max_loss = contexts['max_losses']

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.call_order.delete()
        self.put_order.delete()

    def test_left_break_even(self):
        """
        Left side break even
        """
        print self.left_break_even
        self.assertFalse(self.left_break_even.id)
        self.assertEqual(float(self.left_break_even.price), self.put_order.strike)
        self.assertEqual(self.left_break_even.condition, '>=')
        self.assertEqual(float(self.left_break_even.amount), -340)

    def test_left_start_profit(self):
        """
        Left side start loss
        """
        print self.left_start_profit
        self.assertFalse(self.left_start_profit.id)
        self.assertEqual(float(self.left_start_profit.price),
                         self.put_order.strike)
        self.assertEqual(self.left_start_profit.condition, '<')

    def test_left_max_profit(self):
        """
        Left side max loss
        """
        print self.left_max_profit
        self.assertFalse(self.left_max_profit.id)
        self.assertEqual(float(self.left_max_profit.price),
                         self.put_order.strike * (1 - self.price_range))
        self.assertEqual(self.left_max_profit.condition, '<=')
        self.assertTrue(self.left_max_profit.limit)
        self.assertEqual(float(self.left_max_profit.amount), 10460.0)

    def test_right_break_even(self):
        """
        Right break even
        """
        print self.right_break_even
        self.assertFalse(self.right_break_even.id)
        self.assertEqual(float(self.right_break_even.price), self.call_order.strike)
        self.assertEqual(self.right_break_even.condition, '<=')
        self.assertEqual(self.right_break_even.amount, -340.0)

    def test_right_start_loss(self):
        """
        Right start profit
        """
        print self.right_start_loss
        self.assertFalse(self.right_start_loss.id)
        self.assertEqual(float(self.right_start_loss.price), self.call_order.strike)
        self.assertEqual(self.right_start_loss.condition, '>')

    def test_right_max_loss(self):
        """
        Right max profit
        """
        print self.right_max_loss
        self.assertFalse(self.right_max_loss.id)
        self.assertEqual(self.right_max_loss.price,
                         self.right_break_even.price * Decimal(1 + self.price_range))
        self.assertEqual(self.right_max_loss.condition, '>=')
        self.assertFalse(self.right_max_loss.limit)
        self.assertEqual(self.right_max_loss.amount, -11740.0)

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print '.' * 60
        print self.left_break_even, self.right_break_even
        print self.left_start_profit, self.right_start_profit
        print self.left_start_loss, self.right_start_loss
        print self.left_max_profit, self.right_max_profit
        print self.left_max_loss, self.right_max_loss
