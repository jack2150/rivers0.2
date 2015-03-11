from position.classes.context.tests import *
from position.classes.context.leg_two.strangle.strangle import *


class TestContextLongStrangle(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'call': {'contract': 'CALL', 'side': 'BUY', 'quantity': +1,
                     'strike': 52.5, 'price': 2.06, 'net_price': 0.0},
            'put': {'contract': 'PUT', 'side': 'BUY', 'quantity': +1,
                    'strike': 50, 'price': 2.08, 'net_price': 4.14},
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

        self.long_straddle = ContextLongStrangle(
            filled_orders=filled_orders,
            contract_right=self.contract_right,
            price_range=self.price_range
        )
        self.position_contexts = self.long_straddle.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.call_order.delete()
        self.put_order.delete()

    def test_position_contexts(self):
        """
        Position Contexts that contain 2 position context left and right
        """
        self.assertTrue(self.position_contexts.id)

    def test_position_context_left(self):
        """
        Left position context
        """
        self.assertTrue(self.position_contexts.left.id)

    def test_position_context_right(self):
        """
        Right position context
        """
        self.assertTrue(self.position_contexts.right.id)

    def test_left_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_contexts.left.break_even.id)
        self.assertEqual(float(self.position_contexts.left.break_even.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.left.break_even.condition, '==')

    def test_left_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_contexts.left.start_profit.id)
        self.assertEqual(float(self.position_contexts.left.start_profit.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.left.start_profit.condition, '<')

    def test_left_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_contexts.left.start_loss.id)
        self.assertEqual(float(self.position_contexts.left.start_loss.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.left.start_loss.condition, '>')

    def test_left_max_profit(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_contexts.left.max_profit.id)
        self.assertEqual(self.position_contexts.left.max_profit.price,
                         self.position_contexts.left.break_even.price * Decimal(1 - self.price_range))
        self.assertEqual(self.position_contexts.left.max_profit.condition, '<=')
        self.assertTrue(self.position_contexts.left.max_profit.limit)
        self.assertEqual(float(self.position_contexts.left.max_profit.amount),
                         float(((self.position_contexts.left.break_even.price * Decimal(1 - self.price_range))
                                - self.position_contexts.left.break_even.price)
                               * Decimal(self.contract_right) * -1))

    def test_left_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_contexts.left.max_loss.id)
        self.assertEqual(float(self.position_contexts.left.max_loss.price),
                         self.put_order.strike)
        self.assertEqual(self.position_contexts.left.max_loss.condition, '>=')
        self.assertTrue(self.position_contexts.left.max_loss.limit)
        self.assertEqual(float(self.position_contexts.left.max_loss.amount),
                         float(round(((self.call_order.price + self.put_order.price)
                                      * self.put_order.quantity * self.contract_right * -1), 2)))

    def test_right_break_even(self):
        """
        Right break even
        """
        self.assertTrue(self.position_contexts.right.break_even.id)
        self.assertEqual(float(self.position_contexts.right.break_even.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.right.break_even.condition, '==')

    def test_right_start_profit(self):
        """
        Right start profit
        """
        self.assertTrue(self.position_contexts.right.start_profit.id)
        self.assertEqual(float(self.position_contexts.right.start_profit.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.right.start_profit.condition, '>')

    def test_right_start_loss(self):
        """
        Right start loss
        """
        self.assertTrue(self.position_contexts.right.start_loss.id)
        self.assertEqual(float(self.position_contexts.right.start_loss.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.right.start_loss.condition, '<')

    def test_right_max_profit(self):
        """
        Right max profit
        """

        self.assertTrue(self.position_contexts.right.max_profit.id)
        self.assertEqual(self.position_contexts.right.max_profit.price,
                         self.position_contexts.right.break_even.price * Decimal(1 + self.price_range))
        self.assertEqual(self.position_contexts.right.max_profit.condition, '>=')
        self.assertFalse(self.position_contexts.right.max_profit.limit)
        self.assertEqual(self.position_contexts.right.max_profit.amount,
                         ((self.position_contexts.right.break_even.price * Decimal(1 + self.price_range))
                          - self.position_contexts.right.break_even.price)
                         * Decimal(self.contract_right))

    def test_right_max_loss(self):
        """
        Right max loss
        """
        self.assertTrue(self.position_contexts.right.max_loss.id)
        self.assertEqual(float(self.position_contexts.right.max_loss.price),
                         self.call_order.strike)
        self.assertEqual(self.position_contexts.right.max_loss.condition, '<=')
        self.assertTrue(self.position_contexts.right.max_loss.limit)
        self.assertEqual(float(self.position_contexts.right.max_loss.amount),
                         float(round((self.call_order.price + self.put_order.price)
                                     * self.put_order.quantity * self.contract_right * -1, 2)))

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_contexts
        print '.' * 60
        print self.position_contexts.left.break_even
        print self.position_contexts.left.start_profit
        print self.position_contexts.left.start_loss
        print self.position_contexts.left.max_profit
        print self.position_contexts.left.max_loss
        print '.' * 60
        print self.position_contexts.right.break_even
        print self.position_contexts.right.start_profit
        print self.position_contexts.right.start_loss
        print self.position_contexts.right.max_profit
        print self.position_contexts.right.max_loss


class TestContextShortStraddle(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.orders = {
            'call': {'contract': 'CALL', 'side': 'SELL', 'quantity': -1,
                     'strike': 52.5, 'price': 2.06, 'net_price': 0.0},
            'put': {'contract': 'PUT', 'side': 'SELL', 'quantity': -1,
                    'strike': 50, 'price': 2.08, 'net_price': 4.14},
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

        self.short_straddle = ContextShortStrangle(
            filled_orders=filled_orders,
            contract_right=self.contract_right,
            price_range=self.price_range
        )
        self.position_contexts = self.short_straddle.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.call_order.delete()
        self.put_order.delete()

    def test_position_contexts(self):
        """
        Position Contexts that contain 2 position context left and right
        """
        self.assertTrue(self.position_contexts.id)

    def test_position_context_left(self):
        """
        Left position context
        """
        self.assertTrue(self.position_contexts.left.id)

    def test_position_context_right(self):
        """
        Right position context
        """
        self.assertTrue(self.position_contexts.right.id)

    def test_left_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_contexts.left.break_even.id)
        self.assertTrue(self.position_contexts.left.break_even.id)
        self.assertEqual(float(self.position_contexts.left.break_even.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.left.break_even.condition, '==')

    def test_left_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_contexts.left.start_profit.id)
        self.assertEqual(float(self.position_contexts.left.start_profit.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.left.start_profit.condition, '>')

    def test_left_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_contexts.left.start_loss.id)
        self.assertEqual(float(self.position_contexts.left.start_loss.price),
                         self.put_order.strike - (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.left.start_loss.condition, '<')

    def test_left_max_profit(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_contexts.left.max_profit.id)
        self.assertEqual(self.position_contexts.left.max_profit.price,
                         self.put_order.strike)
        self.assertEqual(self.position_contexts.left.max_profit.condition, '==')
        self.assertTrue(self.position_contexts.left.max_profit.limit)
        self.assertEqual(float(self.position_contexts.left.max_profit.amount),
                         float(round((self.call_order.price + self.put_order.price)
                               * self.put_order.quantity * self.contract_right * -1, 2)))

    def test_left_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_contexts.left.max_loss.id)
        self.assertEqual(float(self.position_contexts.left.max_loss.price),
                         float(self.position_contexts.left.break_even.price
                               * Decimal(1 - self.price_range)))
        self.assertEqual(self.position_contexts.left.max_loss.condition, '<=')
        self.assertTrue(self.position_contexts.left.max_loss.limit)
        self.assertEqual(self.position_contexts.left.max_loss.amount,
                         (((self.position_contexts.left.break_even.price * Decimal(1 - self.price_range))
                           - self.position_contexts.left.break_even.price) * Decimal(self.contract_right)))

    def test_right_break_even(self):
        """
        Right break even
        """
        self.assertTrue(self.position_contexts.right.break_even.id)
        self.assertEqual(float(self.position_contexts.right.break_even.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.right.break_even.condition, '==')

    def test_right_start_profit(self):
        """
        Right start profit
        """
        self.assertTrue(self.position_contexts.right.start_profit.id)
        self.assertEqual(float(self.position_contexts.right.start_profit.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.right.start_profit.condition, '<')

    def test_right_start_loss(self):
        """
        Right start loss
        """
        self.assertTrue(self.position_contexts.right.start_loss.id)
        self.assertEqual(float(self.position_contexts.right.start_loss.price),
                         self.call_order.strike + (self.call_order.price + self.put_order.price))
        self.assertEqual(self.position_contexts.right.start_loss.condition, '>')

    def test_right_max_profit(self):
        """
        Right max profit
        """
        self.assertTrue(self.position_contexts.right.max_profit.id)
        self.assertEqual(self.position_contexts.right.max_profit.price,
                         self.call_order.strike)
        self.assertEqual(self.position_contexts.right.max_profit.condition, '==')
        self.assertTrue(self.position_contexts.right.max_profit.limit)
        self.assertEqual(float(self.position_contexts.right.max_profit.amount),
                         float(round((self.call_order.price + self.put_order.price)
                               * self.put_order.quantity * self.contract_right * -1, 2)))

    def test_right_max_loss(self):
        """
        Right max loss
        """
        self.assertTrue(self.position_contexts.right.max_loss.id)
        self.assertEqual(self.position_contexts.right.max_loss.price,
                         self.position_contexts.right.break_even.price * Decimal(1 + self.price_range))
        self.assertEqual(self.position_contexts.right.max_loss.condition, '>=')
        self.assertFalse(self.position_contexts.right.max_loss.limit)
        self.assertEqual(self.position_contexts.right.max_loss.amount,
                         (((self.position_contexts.right.break_even.price * Decimal(1 + self.price_range))
                           - self.position_contexts.right.break_even.price)
                          * Decimal(self.contract_right) * -1))

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_contexts
        print '.' * 60
        print self.position_contexts.left.break_even
        print self.position_contexts.left.start_profit
        print self.position_contexts.left.start_loss
        print self.position_contexts.left.max_profit
        print self.position_contexts.left.max_loss
        print '.' * 60
        print self.position_contexts.right.break_even
        print self.position_contexts.right.start_profit
        print self.position_contexts.right.start_loss
        print self.position_contexts.right.max_profit
        print self.position_contexts.right.max_loss