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
        self.position_context = self.long_call_vertical.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.buy_order.delete()
        self.sell_order.delete()

    def test_position_context(self):
        """
        Position context
        """
        self.assertTrue(self.position_context.id)
        print self.position_context

    def test_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_context.break_even.id)
        self.assertEqual(float(self.position_context.break_even.price), 81.64)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), 81.64)
        self.assertEqual(self.position_context.start_profit.condition, '>')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), 81.64)
        self.assertEqual(self.position_context.start_loss.condition, '<')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(self.position_context.max_profit.price,
                         self.sell_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount), 336.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(self.position_context.max_loss.price,
                         self.buy_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(float(self.position_context.max_loss.amount), -164.00)
        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print '.' * 60
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss


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
        self.position_context = self.short_call_vertical.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.buy_order.delete()
        self.sell_order.delete()

    def test_position_context(self):
        """
        Position context
        """
        self.assertTrue(self.position_context.id)

    def test_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_context.break_even.id)
        self.assertEqual(float(self.position_context.break_even.price), 77.55)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), 77.55)
        self.assertEqual(self.position_context.start_profit.condition, '<')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), 77.55)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(self.position_context.max_profit.price,
                         self.sell_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount), 245)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(self.position_context.max_loss.price,
                         self.buy_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(float(self.position_context.max_loss.amount), -255)
        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print '.' * 60
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss


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
        self.position_context = self.short_call_vertical.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.buy_order.delete()
        self.sell_order.delete()

    def test_position_context(self):
        """
        Position context
        """
        self.assertTrue(self.position_context.id)

    def test_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_context.break_even.id)
        self.assertEqual(float(self.position_context.break_even.price), 25.45)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), 25.45)
        self.assertEqual(self.position_context.start_profit.condition, '<')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), 25.45)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(self.position_context.max_profit.price,
                         self.sell_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount), 45)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(self.position_context.max_loss.price,
                         self.buy_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(float(self.position_context.max_loss.amount), -55)
        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print '.' * 60
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss


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
        self.position_context = self.short_call_vertical.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.buy_order.delete()
        self.sell_order.delete()

    def test_position_context(self):
        """
        Position context
        """
        self.assertTrue(self.position_context.id)

    def test_break_even(self):
        """
        Left side break even
        """
        self.assertTrue(self.position_context.break_even.id)
        self.assertEqual(float(self.position_context.break_even.price), 25.74)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), 25.74)
        self.assertEqual(self.position_context.start_profit.condition, '>')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), 25.74)
        self.assertEqual(self.position_context.start_loss.condition, '<')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(self.position_context.max_profit.price,
                         self.sell_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount), 126)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max profit
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(self.position_context.max_loss.price,
                         self.buy_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(float(self.position_context.max_loss.amount), -74)
        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print '.' * 60
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss
