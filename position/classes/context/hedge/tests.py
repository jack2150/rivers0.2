from position.classes.tests import create_filled_order, TestUnitSetUp
from position.classes.context.hedge.hedge import *


class TestContextCoveredCall(TestUnitSetUp):
    def test_create_context(self):
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

        self.covered_call = ContextCoveredCall(
            filled_orders=filled_orders
        )
        self.position_context = self.covered_call.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '>')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '<')

        self.assertEqual(float(self.position_context.max_profit.price),
                         self.option_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            float(round((self.option_order.strike - self.stock_order.price
                         + self.option_order.price) * self.stock_order.quantity, 2))
        )

        self.assertEqual(float(self.position_context.max_loss.price),
                         round(self.stock_order.price * 0.5, 2))
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            round(((self.stock_order.price - self.option_order.price) -
                   (self.stock_order.price * 0.5)) * -self.stock_order.quantity, 2)
        )

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.stock_order.delete()
        self.option_order.delete()


class TestContextProtectiveCall(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
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

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.protective_call = ContextProtectiveCall(
            filled_orders=filled_orders
        )
        self.position_context = self.protective_call.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '<')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price - self.option_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '>')

        self.assertEqual(float(self.position_context.max_profit.price),
                         round(self.stock_order.price * 0.5, 2))
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            self.position_context.max_profit.amount,
            round(((self.stock_order.price - self.option_order.price) -
                   (self.stock_order.price * 0.5)) * self.stock_order.quantity, 2)
        )

        self.assertEqual(float(self.position_context.max_loss.price),
                         self.option_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            float(round((self.option_order.strike - self.stock_order.price
                         + self.option_order.price) * -self.stock_order.quantity, 2))
        )

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.stock_order.delete()
        self.option_order.delete()


class TestContextCoveredPut(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
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

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '<')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '>')

        self.assertEqual(float(self.position_context.max_profit.price),
                         self.option_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            float(round((self.option_order.strike - self.stock_order.price - self.option_order.price)
                        * self.stock_order.quantity))
        )

        self.assertEqual(float(self.position_context.max_loss.price),
                         round(self.stock_order.price * 1.5, 2))
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            round(((self.stock_order.price + self.option_order.price)
                   - (self.stock_order.price * 0.5)
                   - self.option_order.price) * self.stock_order.quantity, 2)
        )

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.stock_order.delete()
        self.option_order.delete()


class TestContextProtectivePut(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
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

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.covered_call = ContextProtectivePut(
            filled_orders=filled_orders
        )
        self.position_context = self.covered_call.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '>')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.stock_order.price + self.option_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '<')

        self.assertEqual(float(self.position_context.max_profit.price),
                         round(self.stock_order.price * 1.5, 2))
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            round(((self.stock_order.price + self.option_order.price)
                   - (self.stock_order.price * 0.5)
                   - self.option_order.price) * -self.stock_order.quantity, 2)
        )

        self.assertEqual(float(self.position_context.max_loss.price),
                         self.option_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            float(round((self.option_order.strike - self.stock_order.price - self.option_order.price)
                        * -self.stock_order.quantity))
        )

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.stock_order.delete()
        self.option_order.delete()
