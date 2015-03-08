from position.classes.tests import create_filled_order, TestUnitSetUp
from position.classes.context.equity.equity import *


class TestContextLongStock(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
        self.filled_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='STOCK',
            contract='ETF',
            side='BUY',
            quantity=100
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.long_stock = ContextLongStock(
            filled_orders=filled_orders
        )
        self.position_context = self.long_stock.create_context()
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

        self.assertEqual(float(self.position_context.max_profit.price), self.filled_order.price * 2)
        self.assertEqual(self.position_context.max_profit.condition, '==')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            self.filled_order.price * self.filled_order.quantity * 1
        )

        self.assertEqual(float(self.position_context.max_loss.price), self.filled_order.price * 0)
        self.assertEqual(self.position_context.max_loss.condition, '==')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            self.filled_order.price * self.filled_order.quantity * -1
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
            underlying=self.underlying,
            spread='STOCK',
            contract='ETF',
            side='SELL',
            quantity=-100
        )

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.short_stock = ContextShortStock(
            filled_orders=filled_orders
        )
        self.position_context = self.short_stock.create_context()
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

        self.assertEqual(float(self.position_context.max_profit.price), self.filled_order.price * 0.0)
        self.assertEqual(self.position_context.max_profit.condition, '==')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            self.filled_order.price * self.filled_order.quantity * 1
        )

        self.assertEqual(float(self.position_context.max_loss.price), self.filled_order.price * 2)
        self.assertEqual(self.position_context.max_loss.condition, '==')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            self.filled_order.price * self.filled_order.quantity * -1
        )

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.filled_order.delete()
