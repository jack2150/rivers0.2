from position.classes.tests import create_filled_order, TestUnitSetUp
from position.classes.context.future.future import *


class TestContextLongFuture(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
        self.filled_order = create_filled_order(
            trade_summary=self.trade_summary,
            future=self.future,
            spread='FUTURE',
            contract='FUTURE',
            side='BUY',
            quantity=1,
            price=480.00,
            net_price=480.00
        )

        filled_orders = FilledOrder.objects.filter(future=self.future).all()

        self.long_future = ContextLongFuture(
            filled_orders=filled_orders
        )
        self.position_context = self.long_future.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price), self.filled_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.start_profit.price), self.filled_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '>')

        self.assertEqual(float(self.position_context.start_loss.price), self.filled_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '<')

        spc = float(Fraction(self.future.spc))
        self.assertEqual(float(self.position_context.max_profit.price), self.filled_order.price * 2)
        self.assertEqual(self.position_context.max_profit.condition, '==')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            float(self.filled_order.price * self.filled_order.quantity) / spc
        )

        self.assertEqual(float(self.position_context.max_loss.price), self.filled_order.price * 0)
        self.assertEqual(self.position_context.max_loss.condition, '==')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            float(self.filled_order.price * self.filled_order.quantity) / -spc
        )

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.filled_order.delete()


class TestContextShortStock(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
        self.filled_order = create_filled_order(
            trade_summary=self.trade_summary,
            future=self.future,
            spread='FUTURE',
            contract='FUTURE',
            side='SELL',
            quantity=-1,
            price=484.25,
            net_price=484.25
        )

        filled_orders = FilledOrder.objects.filter(future=self.future).all()

        self.short_future = ContextShortFuture(
            filled_orders=filled_orders
        )
        self.position_context = self.short_future.create_context()
        self.assertTrue(self.position_context)
        self.assertTrue(self.position_context.break_even.id)
        self.assertTrue(self.position_context.start_profit.id)
        self.assertTrue(self.position_context.start_loss.id)
        self.assertTrue(self.position_context.max_profit.id)
        self.assertTrue(self.position_context.max_loss.id)

        self.assertEqual(float(self.position_context.break_even.price), self.filled_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')

        self.assertEqual(float(self.position_context.start_profit.price), self.filled_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '<')

        self.assertEqual(float(self.position_context.start_loss.price), self.filled_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '>')

        spc = float(Fraction(self.future.spc))
        self.assertEqual(float(self.position_context.max_profit.price), self.filled_order.price * 0)
        self.assertEqual(self.position_context.max_profit.condition, '==')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            float(self.filled_order.price * self.filled_order.quantity) / -spc
        )

        self.assertEqual(float(self.position_context.max_loss.price), self.filled_order.price * 2)
        self.assertEqual(self.position_context.max_loss.condition, '==')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            float(self.filled_order.price * self.filled_order.quantity) / spc
        )

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.filled_order.delete()
