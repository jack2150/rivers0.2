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

        self.position_context = self.covered_call.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()
        self.option_order.delete()

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
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 83.3)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 83.3)
        self.assertEqual(self.position_context.start_profit.condition, '>')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 83.3)
        self.assertEqual(self.position_context.start_loss.condition, '<')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         self.option_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            float(round((self.option_order.strike - self.stock_order.price
                         + self.option_order.price) * self.stock_order.quantity, 2))
        )
        self.assertEqual(float(self.position_context.max_profit.amount), 170.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price), 68.4)
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            round(self.position_context.max_loss.amount, 2),
            round(
                (float(self.position_context.break_even.price)
                 - (self.stock_order.price * (1 - self.price_range)))
                * self.stock_order.quantity * -1, 2
            )
        )
        self.assertEqual(round(self.position_context.max_loss.amount, 2), -1490.00)
        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss


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
        self.position_context = self.protective_call.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()
        self.option_order.delete()

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
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '<')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         self.stock_order.price * (1 - self.price_range))
        self.assertEqual(float(self.position_context.max_profit.price), 68.4)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            round(self.position_context.max_profit.amount, 2),
            round(
                (float(self.position_context.break_even.price) -
                 (self.stock_order.price * (1 - self.price_range)))
                * self.stock_order.quantity, 2
            )
        )
        self.assertEqual(round(self.position_context.max_profit.amount, 2), 1490.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price), self.option_order.strike)
        self.assertEqual(float(self.position_context.max_loss.price), 85.0)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            round(self.position_context.max_loss.amount, 2),
            round(
                (self.option_order.strike - self.stock_order.price + self.option_order.price)
                * self.stock_order.quantity * -1, 2
            )
        )
        self.assertEqual(float(self.position_context.max_loss.amount), -170.00)

        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss


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
        self.position_context = self.covered_call.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()
        self.option_order.delete()

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
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '<')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         self.option_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            float(round((self.option_order.strike - self.stock_order.price - self.option_order.price)
                        * self.stock_order.quantity))
        )
        self.assertEqual(round(self.position_context.max_profit.amount, 2), 270.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         self.stock_order.price * (1 + self.price_range))
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(
            round(self.position_context.max_loss.amount, 2),
            round(
                (float(self.position_context.break_even.price) -
                 (self.stock_order.price * (1 + self.price_range)))
                * self.stock_order.quantity * -1, 2
            )
        )
        self.assertEqual(round(self.position_context.max_loss.amount, 2), -1490.00)

        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss


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
        self.position_context = self.protective_put.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.stock_order.delete()
        self.option_order.delete()

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
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 87.7)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 87.7)
        self.assertEqual(self.position_context.start_profit.condition, '>')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 87.7)
        self.assertEqual(self.position_context.start_loss.condition, '<')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)

        self.assertEqual(float(self.position_context.max_profit.price),
                         self.stock_order.price * (1 - self.price_range))
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            round(self.position_context.max_profit.amount, 2),
            round(
                ((self.stock_order.price * (1 - self.price_range)) -
                 float(self.position_context.break_even.price))
                * self.stock_order.quantity, 2
            )
        )
        self.assertEqual(round(self.position_context.max_profit.amount, 2), 1930.00)

        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         self.option_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            float(round((self.option_order.strike - self.stock_order.price - self.option_order.price)
                        * self.stock_order.quantity * -1))
        )
        self.assertEqual(round(self.position_context.max_loss.amount, 2), -270.00)
        print self.position_context.max_loss

    def test_output(self):
        """
        Output all contexts
        """
        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss