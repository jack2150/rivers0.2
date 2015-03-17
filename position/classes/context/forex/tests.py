from position.classes.context.tests import TestUnitSetUpDB
from position.classes.tests import create_filled_order
from position.classes.context.forex.forex import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongForex(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.forex_order = create_filled_order(
            trade_summary=self.trade_summary,
            forex=self.forex,
            spread='FOREX',
            contract='FOREX',
            side='BUY',
            quantity=10000,
            price=120.1295
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(forex=self.forex).all()

        self.long_forex = ContextLongForex(
            filled_orders=filled_orders
        )
        self.position_context = self.long_forex.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.forex_order.delete()

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
        self.assertEqual(float(self.position_context.break_even.price), self.forex_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 120.1295)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), self.forex_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 120.1295)
        self.assertEqual(self.position_context.start_profit.condition, '>')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), self.forex_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 120.1295)
        self.assertEqual(self.position_context.start_loss.condition, '<')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         round(self.forex_order.price * (1 + self.price_range), 6))
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(
            float(round(self.position_context.max_profit.amount, 2)),
            round(((self.forex_order.price * (1 + self.price_range) * self.forex_order.quantity)
                   - (self.forex_order.price * self.forex_order.quantity))
                  / (self.forex_order.price * (1 + self.price_range)), 2)
        )
        self.assertEqual(round(self.position_context.max_profit.amount, 2), 1666.67)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         self.forex_order.price * (1 - self.price_range))
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            round(self.position_context.max_loss.amount, 2),
            round(
                ((self.forex_order.price * (1 - self.price_range) * self.forex_order.quantity)
                 - (self.forex_order.price * self.forex_order.quantity))
                / (self.forex_order.price * (1 - self.price_range)), 2
            )
        )
        self.assertEqual(round(self.position_context.max_loss.amount, 2), -2500.00)

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


class TestContextShortFuture(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.forex_order = create_filled_order(
            trade_summary=self.trade_summary,
            forex=self.forex,
            spread='FOREX',
            contract='FOREX',
            side='SELL',
            quantity=-10000,
            price=120.1295
        )

        self.price_range = 0.2

        filled_orders = FilledOrder.objects.filter(forex=self.forex).all()

        self.short_forex = ContextShortForex(
            filled_orders=filled_orders
        )
        self.position_context = self.short_forex.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.forex_order.delete()

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
        self.assertEqual(float(self.position_context.break_even.price), self.forex_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 120.1295)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), self.forex_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 120.1295)
        self.assertEqual(self.position_context.start_profit.condition, '<')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), self.forex_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 120.1295)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         self.forex_order.price * (1 - self.price_range))
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            round(self.position_context.max_profit.amount, 2),
            round(
                ((self.forex_order.price * (1 - self.price_range) * self.forex_order.quantity)
                 - (self.forex_order.price * self.forex_order.quantity))
                / (self.forex_order.price * (1 - self.price_range)), 2
            )
        )
        self.assertEqual(round(self.position_context.max_profit.amount, 2), 2500.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         round(self.forex_order.price * (1 + self.price_range), 6))
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(
            float(round(self.position_context.max_loss.amount, 2)),
            round(((self.forex_order.price * (1 + self.price_range) * self.forex_order.quantity)
                   - (self.forex_order.price * self.forex_order.quantity))
                  / (self.forex_order.price * (1 + self.price_range)), 2)
        )
        self.assertEqual(round(self.position_context.max_loss.amount, 2), -1666.67)
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