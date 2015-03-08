from position.classes.tests import create_filled_order, TestUnitSetUp
from position.classes.context.forex.forex import *


class TestContextLongForex(TestUnitSetUp):
    def test_create_context(self):
        """
        Test create context data using filled orders
        """
        self.filled_order = create_filled_order(
            trade_summary=self.trade_summary,
            forex=self.forex,
            spread='FOREX',
            contract='FOREX',
            side='BUY',
            quantity=10000,
            price=120.1295
        )

        filled_orders = FilledOrder.objects.filter(forex=self.forex).all()

        self.long_forex = ContextLongForex(
            filled_orders=filled_orders
        )
        self.position_context = self.long_forex.create_context()
        self.assertTrue(self.position_context.id)
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

        self.assertEqual(float(self.position_context.max_profit.price),
                         round(self.filled_order.price * 1.5, 6))
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(
            round(float(self.position_context.max_profit.amount), 2),
            round(((self.filled_order.price * 1.5 * self.filled_order.quantity)
                   - (self.filled_order.price * self.filled_order.quantity))
                  / (self.filled_order.price * 1.5), 2)
        )

        self.assertEqual(float(self.position_context.max_loss.price),
                         self.filled_order.price * 0.5)
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            round(
                ((self.filled_order.price * 0.5 * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / (self.filled_order.price * 0.5), 5
            )
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
            forex=self.forex,
            spread='FOREX',
            contract='FOREX',
            side='SELL',
            quantity=-10000,
            price=120.1295
        )

        filled_orders = FilledOrder.objects.filter(forex=self.forex).all()

        self.short_forex = ContextShortForex(
            filled_orders=filled_orders
        )
        self.position_context = self.short_forex.create_context()
        self.assertTrue(self.position_context.id)
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

        self.assertEqual(float(self.position_context.max_loss.price),
                         round(self.filled_order.price * 1.5, 6))
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(
            float(round(self.position_context.max_loss.amount, 2)),
            round(((self.filled_order.price * 1.5 * self.filled_order.quantity)
                   - (self.filled_order.price * self.filled_order.quantity))
                  / (self.filled_order.price * 1.5), 2)
        )

        self.assertEqual(float(self.position_context.max_profit.price),
                         self.filled_order.price * 0.5)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            round(
                ((self.filled_order.price * 0.5 * self.filled_order.quantity)
                 - (self.filled_order.price * self.filled_order.quantity))
                / (self.filled_order.price * 0.5), 5
            )
        )

        print 'position context...'
        print self.position_context
        print self.position_context.break_even
        print self.position_context.start_profit
        print self.position_context.start_loss
        print self.position_context.max_profit
        print self.position_context.max_loss

        self.filled_order.delete()
