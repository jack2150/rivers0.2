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
        self.position_contexts = self.long_combo.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.call_order.delete()
        self.put_order.delete()

    def test_position_contexts(self):
        """
        Position Contexts that contain 2 position context left and right
        """
        self.assertTrue(self.position_contexts.id)
        print 'position_contexts id: %d' % self.position_contexts.id

    def test_position_context_left(self):
        """
        Left position context
        """
        self.assertTrue(self.position_contexts.left.id)
        print 'position_context left id: %d' % self.position_contexts.left.id

    def test_position_context_right(self):
        """
        Right position context
        """
        self.assertTrue(self.position_contexts.right.id)
        print 'position_context right id: %d' % self.position_contexts.right.id

    def test_left_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_contexts.left.break_even.id)
        self.assertEqual(float(self.position_contexts.left.break_even.price), self.put_order.strike)
        self.assertEqual(self.position_contexts.left.break_even.condition, '>=')
        self.assertEqual(float(self.position_contexts.left.break_even.amount), 10.00)
        print self.position_contexts.left.break_even

    def test_left_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_contexts.left.start_loss.id)
        self.assertEqual(float(self.position_contexts.left.start_loss.price),
                         self.put_order.strike)
        self.assertEqual(self.position_contexts.left.start_loss.condition, '<')
        print self.position_contexts.left.start_loss

    def test_left_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_contexts.left.max_loss.id)
        self.assertEqual(float(self.position_contexts.left.max_loss.price),
                         self.put_order.strike * (1 - self.price_range))
        self.assertEqual(self.position_contexts.left.max_loss.condition, '<=')
        self.assertTrue(self.position_contexts.left.max_loss.limit)
        self.assertEqual(float(self.position_contexts.left.max_loss.amount), -970.00)
        print self.position_contexts.left.max_loss

    def test_right_break_even(self):
        """
        Right break even
        """
        self.assertTrue(self.position_contexts.right.break_even.id)
        self.assertEqual(float(self.position_contexts.right.break_even.price), self.call_order.strike)
        self.assertEqual(self.position_contexts.right.break_even.condition, '<=')
        self.assertEqual(self.position_contexts.right.break_even.amount, 10.00)
        print self.position_contexts.right.break_even

    def test_right_start_profit(self):
        """
        Right start profit
        """
        self.assertTrue(self.position_contexts.right.start_profit.id)
        self.assertEqual(float(self.position_contexts.right.start_profit.price), self.call_order.strike)
        self.assertEqual(self.position_contexts.right.start_profit.condition, '>')
        print self.position_contexts.right.start_profit

    def test_right_max_profit(self):
        """
        Right max profit
        """

        self.assertTrue(self.position_contexts.right.max_profit.id)
        self.assertEqual(self.position_contexts.right.max_profit.price,
                         self.position_contexts.right.break_even.price * Decimal(1 + self.price_range))
        self.assertEqual(self.position_contexts.right.max_profit.condition, '>=')
        self.assertFalse(self.position_contexts.right.max_profit.limit)
        self.assertEqual(self.position_contexts.right.max_profit.amount, 1110.00)
        print self.position_contexts.right.max_profit

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_contexts
        print '.' * 60
        print self.position_contexts.left.break_even
        print self.position_contexts.left.start_loss
        print self.position_contexts.left.max_loss
        print '.' * 60
        print self.position_contexts.right.break_even
        print self.position_contexts.right.start_profit
        print self.position_contexts.right.max_profit


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
        self.position_contexts = self.long_combo.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.call_order.delete()
        self.put_order.delete()

    def test_position_contexts(self):
        """
        Position Contexts that contain 2 position context left and right
        """
        self.assertTrue(self.position_contexts.id)
        print 'position_contexts id: %d' % self.position_contexts.id

    def test_position_context_left(self):
        """
        Left position context
        """
        self.assertTrue(self.position_contexts.left.id)
        print 'position_context left id: %d' % self.position_contexts.left.id

    def test_position_context_right(self):
        """
        Right position context
        """
        self.assertTrue(self.position_contexts.right.id)
        print 'position_context right id: %d' % self.position_contexts.right.id

    def test_left_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_contexts.left.break_even.id)
        self.assertEqual(float(self.position_contexts.left.break_even.price), self.put_order.strike)
        self.assertEqual(self.position_contexts.left.break_even.condition, '>=')
        self.assertEqual(float(self.position_contexts.left.break_even.amount), -340)
        print self.position_contexts.left.break_even

    def test_left_start_profit(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_contexts.left.start_profit.id)
        self.assertEqual(float(self.position_contexts.left.start_profit.price),
                         self.put_order.strike)
        self.assertEqual(self.position_contexts.left.start_profit.condition, '<')
        print self.position_contexts.left.start_profit

    def test_left_max_profit(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_contexts.left.max_profit.id)
        self.assertEqual(float(self.position_contexts.left.max_profit.price),
                         self.put_order.strike * (1 - self.price_range))
        self.assertEqual(self.position_contexts.left.max_profit.condition, '<=')
        self.assertTrue(self.position_contexts.left.max_profit.limit)
        self.assertEqual(float(self.position_contexts.left.max_profit.amount), 10460.0)
        print self.position_contexts.left.max_profit

    def test_right_break_even(self):
        """
        Right break even
        """
        self.assertTrue(self.position_contexts.right.break_even.id)
        self.assertEqual(float(self.position_contexts.right.break_even.price), self.call_order.strike)
        self.assertEqual(self.position_contexts.right.break_even.condition, '<=')
        self.assertEqual(self.position_contexts.right.break_even.amount, -340.0)
        print self.position_contexts.right.break_even

    def test_right_start_loss(self):
        """
        Right start profit
        """
        self.assertTrue(self.position_contexts.right.start_loss.id)
        self.assertEqual(float(self.position_contexts.right.start_loss.price), self.call_order.strike)
        self.assertEqual(self.position_contexts.right.start_loss.condition, '>')
        print self.position_contexts.right.start_loss

    def test_right_max_loss(self):
        """
        Right max profit
        """
        self.assertTrue(self.position_contexts.right.max_loss.id)
        self.assertEqual(self.position_contexts.right.max_loss.price,
                         self.position_contexts.right.break_even.price * Decimal(1 + self.price_range))
        self.assertEqual(self.position_contexts.right.max_loss.condition, '>=')
        self.assertFalse(self.position_contexts.right.max_loss.limit)
        self.assertEqual(self.position_contexts.right.max_loss.amount, -11740.0)
        print self.position_contexts.right.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_contexts
        print '.' * 60
        print self.position_contexts.left.break_even
        print self.position_contexts.left.start_profit
        print self.position_contexts.left.max_profit
        print '.' * 60
        print self.position_contexts.right.break_even
        print self.position_contexts.right.start_loss
        print self.position_contexts.right.max_loss