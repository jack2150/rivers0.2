from position.classes.tests import create_filled_order, TestUnitSetUp
from position.classes.context.option.option import *


class TestContextLongCall(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
        self.filled_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='CALL',
            side='BUY',
            quantity=2,
            strike=58,
            price=0.95
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.long_call = ContextLongCall(
            filled_orders=filled_orders
        )
        self.position_context = self.long_call.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price),
                         self.filled_order.strike + self.filled_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.filled_order.strike + self.filled_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '>')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.filled_order.strike + self.filled_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '<')

        self.assertEqual(float(self.position_context.max_profit.price),
                         self.filled_order.strike + (self.filled_order.price * 10))
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            self.filled_order.price * self.filled_order.quantity * 10 * 100
        )

        self.assertEqual(float(self.position_context.max_loss.price), self.filled_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(self.position_context.max_loss.amount,
                         self.filled_order.price * self.filled_order.quantity * -100)

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.filled_order.delete()


class TestContextNakedCall(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
        self.filled_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='CALL',
            side='SELL',
            quantity=-4,
            strike=100,
            price=2.9
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.naked_call = ContextNakedCall(
            filled_orders=filled_orders
        )
        self.position_context = self.naked_call.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price),
                         self.filled_order.strike + self.filled_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.filled_order.strike + self.filled_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '<')

        self.assertEqual(float(self.position_context.break_even.price),
                         self.filled_order.strike + self.filled_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '>')

        self.assertEqual(float(self.position_context.max_loss.price),
                         self.filled_order.strike + (self.filled_order.price * 10))
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(float(self.position_context.max_loss.amount),
                         self.filled_order.price * self.filled_order.quantity * 10 * 100)

        self.assertEqual(float(self.position_context.max_profit.price), self.filled_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount),
                         self.filled_order.price * self.filled_order.quantity * 100)

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.filled_order.delete()


class TestContextLongPut(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
        self.filled_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='BUY',
            quantity=5,
            strike=58,
            price=3.00
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.long_put = ContextLongPut(
            filled_orders=filled_orders
        )
        self.position_context = self.long_put.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price),
                         self.filled_order.strike - self.filled_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.start_profit.price),
                         self.filled_order.strike - self.filled_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '<')

        self.assertEqual(float(self.position_context.start_loss.price),
                         self.filled_order.strike - self.filled_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '>')

        self.assertEqual(float(self.position_context.max_profit.price), 0.0)
        self.assertEqual(self.position_context.max_profit.condition, '==')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount),
                         (self.filled_order.strike - self.filled_order.price)
                         * self.filled_order.quantity * 100)

        self.assertEqual(float(self.position_context.max_loss.price), self.filled_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(self.position_context.max_loss.amount,
                         self.filled_order.price * self.filled_order.quantity * -100)

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.filled_order.delete()


class TestContextNakedPut(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
        self.filled_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='SELL',
            quantity=-9,
            strike=32,
            price=1.70
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.naked_put = ContextNakedPut(
            filled_orders=filled_orders
        )
        self.position_context = self.naked_put.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price),
                         self.filled_order.strike - self.filled_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.start_profit.price),
                         self.filled_order.strike - self.filled_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '>')

        self.assertEqual(float(self.position_context.start_loss.price),
                         self.filled_order.strike - self.filled_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '<')

        self.assertEqual(float(self.position_context.max_loss.price), 0.0)
        self.assertEqual(self.position_context.max_loss.condition, '==')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(float(self.position_context.max_loss.amount),
                         (self.filled_order.strike - self.filled_order.price)
                         * self.filled_order.quantity * 100)

        self.assertEqual(float(self.position_context.max_profit.price), self.filled_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(self.position_context.max_profit.amount,
                         self.filled_order.price * self.filled_order.quantity * -100)

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.filled_order.delete()
