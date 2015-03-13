from position.classes.context.tests import TestUnitSetUpDB
from position.classes.tests import create_filled_order
from position.classes.context.future.future import *


class TestContextLongFuture(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.future_order = create_filled_order(
            trade_summary=self.trade_summary,
            future=self.future,
            spread='FUTURE',
            contract='FUTURE',
            side='BUY',
            quantity=1,
            price=480.00,
            net_price=480.00
        )

        self.price_range = 0.2
        self.spc = float(Fraction(self.future.spc))

        filled_orders = FilledOrder.objects.filter(future=self.future).all()

        self.long_future = ContextLongFuture(
            filled_orders=filled_orders
        )
        self.position_context = self.long_future.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.future_order.delete()

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
        self.assertEqual(float(self.position_context.break_even.price), self.future_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 480.00)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), self.future_order.price)
        self.assertEqual(float(self.position_context.start_profit.price), 480.00)
        self.assertEqual(self.position_context.start_profit.condition, '>')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), self.future_order.price)
        self.assertEqual(float(self.position_context.start_loss.price), 480.00)
        self.assertEqual(self.position_context.start_loss.condition, '<')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         self.future_order.price * (1 + self.price_range))
        self.assertEqual(self.position_context.max_profit.condition, '==')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            float(self.future_order.price * self.price_range) / self.spc
        )
        self.assertEqual(round(self.position_context.max_profit.amount, 2), 4800.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         self.future_order.price * (1 - self.price_range))
        self.assertEqual(self.position_context.max_loss.condition, '==')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            float(self.future_order.price * self.price_range) / -self.spc
        )
        self.assertEqual(round(self.position_context.max_loss.amount, 2), -4800.00)
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

        self.future_order = create_filled_order(
            trade_summary=self.trade_summary,
            future=self.future,
            spread='FUTURE',
            contract='FUTURE',
            side='SELL',
            quantity=-1,
            price=484.25,
            net_price=484.25
        )

        self.price_range = 0.2
        self.spc = float(Fraction(self.future.spc))

        filled_orders = FilledOrder.objects.filter(future=self.future).all()

        self.short_future = ContextShortFuture(
            filled_orders=filled_orders
        )
        self.position_context = self.short_future.create_context()
        self.spc = float(Fraction(self.future.spc))

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

        self.future_order.delete()

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
        self.assertEqual(float(self.position_context.break_even.price), self.future_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 484.25)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price), self.future_order.price)
        self.assertEqual(float(self.position_context.start_profit.price), 484.25)
        self.assertEqual(self.position_context.start_profit.condition, '<')

        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price), self.future_order.price)
        self.assertEqual(float(self.position_context.start_loss.price), 484.25)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(round(self.position_context.max_profit.price, 2),
                         round(self.future_order.price * (1 - self.price_range), 2))
        self.assertEqual(self.position_context.max_profit.condition, '==')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            (
                (self.future_order.price * self.price_range
                 * self.future_order.quantity) / -self.spc
            )
        )
        self.assertEqual(round(self.position_context.max_profit.amount, 2), 4842.5)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         self.future_order.price * (1 + self.price_range))
        self.assertEqual(self.position_context.max_loss.condition, '==')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(
            float(self.position_context.max_loss.amount),
            (
                (self.future_order.price * self.price_range
                 * self.future_order.quantity) / self.spc
            )
        )
        self.assertEqual(round(self.position_context.max_loss.amount, 2), -4842.5)
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
