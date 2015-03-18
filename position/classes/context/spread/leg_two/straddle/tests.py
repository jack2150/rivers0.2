from position.classes.context.tests import *
from position.classes.context.spread.leg_two.straddle.straddle import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongStraddle(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                     'strike': 85, 'price': 2.25, 'net_price': 0.0},
            'put': {'contract': 'PUT', 'side': 'BUY', 'quantity': +1,
                    'strike': 85, 'price': 2.04, 'net_price': 4.29},
        }

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRADDLE',
            contract=self.orders['call']['contract'],
            side=self.orders['call']['side'],
            quantity=self.orders['call']['quantity'],
            strike=self.orders['call']['strike'],
            price=self.orders['call']['price'],
            net_price=self.orders['call']['net_price']
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRADDLE',
            contract=self.orders['put']['contract'],
            side=self.orders['put']['side'],
            quantity=self.orders['put']['quantity'],
            strike=self.orders['put']['strike'],
            price=self.orders['put']['price'],
            net_price=self.orders['put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100
        self.price_range = 0.2

        self.long_straddle = ContextLongStraddle(
            filled_orders=filled_orders,
            contract_right=self.contract_right,
            price_range=self.price_range
        )
        contexts = self.long_straddle.create_context()

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
        self.assertEqual(float(self.left_break_even.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.left_break_even.condition, '==')

    def test_left_start_profit(self):
        """
        Left side start profit
        """
        print self.left_start_profit
        self.assertFalse(self.left_start_profit.id)
        self.assertEqual(float(self.left_start_profit.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.left_start_profit.condition, '<')

    def test_left_start_loss(self):
        """
        Left side start loss
        """
        print self.left_start_loss
        self.assertFalse(self.left_start_loss.id)
        self.assertEqual(float(self.left_start_loss.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.left_start_loss.condition, '>')

    def test_left_max_profit(self):
        """
        Left side max profit
        """
        print self.left_max_profit
        self.assertFalse(self.left_max_profit.id)
        self.assertEqual(self.left_max_profit.price,
                         self.left_break_even.price * Decimal(1 - self.price_range))
        self.assertEqual(self.left_max_profit.condition, '<=')
        self.assertTrue(self.left_max_profit.limit)
        self.assertEqual(float(self.left_max_profit.amount),
                         float(((self.left_break_even.price * Decimal(1 - self.price_range))
                                - self.left_break_even.price)
                               * Decimal(self.contract_right) * -1))

    def test_left_max_loss(self):
        """
        Left side max loss
        """
        print self.left_max_loss
        self.assertFalse(self.left_max_loss.id)
        self.assertEqual(float(self.left_max_loss.price),
                         self.put_order.strike)
        self.assertEqual(self.left_max_loss.condition, '==')
        self.assertTrue(self.left_max_loss.limit)
        self.assertEqual(float(self.left_max_loss.amount),
                         ((self.call_order.price + self.put_order.price)
                          * self.put_order.quantity * self.contract_right * -1))

    def test_right_break_even(self):
        """
        Right break even
        """
        print self.right_break_even
        self.assertFalse(self.right_break_even.id)
        self.assertEqual(float(self.right_break_even.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.right_break_even.condition, '==')

    def test_right_start_profit(self):
        """
        Right start profit
        """
        print self.right_start_profit
        self.assertFalse(self.right_start_profit.id)
        self.assertEqual(float(self.right_start_profit.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.right_start_profit.condition, '>')

    def test_right_start_loss(self):
        """
        Right start loss
        """
        print self.right_start_loss
        self.assertFalse(self.right_start_loss.id)
        self.assertEqual(float(self.right_start_loss.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.right_start_loss.condition, '<')

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
        self.assertEqual(self.right_max_profit.amount,
                         ((self.right_break_even.price * Decimal(1 + self.price_range))
                          - self.right_break_even.price)
                         * Decimal(self.contract_right))

    def test_right_max_loss(self):
        """
        Right max loss
        """
        print self.right_max_loss
        self.assertFalse(self.right_max_loss.id)
        self.assertEqual(float(self.right_max_loss.price),
                         self.call_order.strike)
        self.assertEqual(self.right_max_loss.condition, '==')
        self.assertTrue(self.right_max_loss.limit)
        self.assertEqual(float(self.right_max_loss.amount),
                         ((self.call_order.price + self.put_order.price)
                          * self.put_order.quantity * self.contract_right * -1))

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


class TestContextShortStraddle(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'call': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1,
                     'strike': 85, 'price': 2.25, 'net_price': 0.0},
            'put': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                    'strike': 85, 'price': 2.04, 'net_price': 4.29},
        }

        self.call_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRADDLE',
            contract=self.orders['call']['contract'],
            side=self.orders['call']['side'],
            quantity=self.orders['call']['quantity'],
            strike=self.orders['call']['strike'],
            price=self.orders['call']['price'],
            net_price=self.orders['call']['net_price']
        )

        self.put_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STRADDLE',
            contract=self.orders['put']['contract'],
            side=self.orders['put']['side'],
            quantity=self.orders['put']['quantity'],
            strike=self.orders['put']['strike'],
            price=self.orders['put']['price'],
            net_price=self.orders['put']['net_price']
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.contract_right = 100
        self.price_range = 0.2

        self.short_straddle = ContextShortStraddle(
            filled_orders=filled_orders,
            contract_right=self.contract_right,
            price_range=self.price_range
        )
        contexts = self.short_straddle.create_context()

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
        self.assertEqual(float(self.left_break_even.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.left_break_even.condition, '==')

    def test_left_start_profit(self):
        """
        Left side start profit
        """
        print self.left_start_profit
        self.assertFalse(self.left_start_profit.id)
        self.assertEqual(float(self.left_start_profit.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.left_start_profit.condition, '>')

    def test_left_start_loss(self):
        """
        Left side start loss
        """
        print self.left_start_loss
        self.assertFalse(self.left_start_loss.id)
        self.assertEqual(float(self.left_start_loss.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.left_start_loss.condition, '<')

    def test_left_max_profit(self):
        """
        Left side max profit
        """
        print self.left_max_profit
        self.assertFalse(self.left_max_profit.id)
        self.assertEqual(self.left_max_profit.price,
                         self.put_order.strike)
        self.assertEqual(self.left_max_profit.condition, '==')
        self.assertTrue(self.left_max_profit.limit)
        self.assertEqual(float(self.left_max_profit.amount),
                         float((self.call_order.price + self.put_order.price)
                               * self.put_order.quantity * self.contract_right * -1))

    def test_left_max_loss(self):
        """
        Left side max loss
        """
        print self.left_max_loss
        self.assertFalse(self.left_max_loss.id)
        self.assertEqual(float(self.left_max_loss.price),
                         float(self.left_break_even.price
                               * Decimal(1 - self.price_range)))
        self.assertEqual(self.left_max_loss.condition, '<=')
        self.assertTrue(self.left_max_loss.limit)
        self.assertEqual(self.left_max_loss.amount,
                         (((self.left_break_even.price * Decimal(1 - self.price_range))
                           - self.left_break_even.price) * Decimal(self.contract_right)))

    def test_right_break_even(self):
        """
        Right break even
        """
        print self.right_break_even
        self.assertFalse(self.right_break_even.id)
        self.assertEqual(float(self.right_break_even.price),
                         self.put_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.right_break_even.condition, '==')

    def test_right_start_profit(self):
        """
        Right start profit
        """
        print self.right_start_profit
        self.assertFalse(self.right_start_profit.id)
        self.assertEqual(float(self.right_start_profit.price),
                         self.put_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.right_start_profit.condition, '<')

    def test_right_start_loss(self):
        """
        Right start loss
        """
        print self.right_start_loss
        self.assertFalse(self.right_start_loss.id)
        self.assertEqual(float(self.right_start_loss.price),
                         self.put_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.right_start_loss.condition, '>')

    def test_right_max_profit(self):
        """
        Right max profit
        """
        print self.right_max_profit
        self.assertFalse(self.right_max_profit.id)
        self.assertEqual(self.right_max_profit.price,
                         self.call_order.strike)
        self.assertEqual(self.right_max_profit.condition, '==')
        self.assertTrue(self.right_max_profit.limit)
        self.assertEqual(self.right_max_profit.amount,
                         ((self.call_order.price + self.put_order.price)
                          * self.put_order.quantity * self.contract_right * -1))

    def test_right_max_loss(self):
        """
        Right max loss
        """
        print self.right_max_loss
        self.assertFalse(self.right_max_loss.id)
        self.assertEqual(self.right_max_loss.price,
                         self.right_break_even.price * Decimal(1 + self.price_range))
        self.assertEqual(self.right_max_loss.condition, '>=')
        self.assertFalse(self.right_max_loss.limit)
        self.assertEqual(self.right_max_loss.amount,
                         (((self.right_break_even.price * Decimal(1 + self.price_range))
                           - self.right_break_even.price)
                          * Decimal(self.contract_right) * -1))

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


