from position.classes.context.tests import TestUnitSetUpDB
from position.classes.tests import create_filled_order
from position.classes.context.option.option import *
from tos_import.statement.statement_trade.models import FilledOrder


class TestContextLongCall(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='CALL',
            side='BUY',
            quantity=2,
            strike=58,
            price=0.95
        )

        self.contract_right = 100
        self.price_multiply = 10

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.long_call = ContextLongCall(
            filled_orders=filled_orders
        )
        self.position_context = self.long_call.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

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
                         self.option_order.strike + self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 58.95)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price),
                         self.option_order.strike + self.option_order.price)
        self.assertEqual(float(self.position_context.start_profit.price), 58.95)
        self.assertEqual(self.position_context.start_profit.condition, '>')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price),
                         self.option_order.strike + self.option_order.price)
        self.assertEqual(float(self.position_context.start_loss.price), 58.95)
        self.assertEqual(self.position_context.start_loss.condition, '<')

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         self.option_order.strike + (self.option_order.price * self.price_multiply))
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertFalse(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount),
                         self.option_order.price * self.option_order.quantity
                         * self.price_multiply * self.contract_right)
        self.assertEqual(float(self.position_context.max_profit.amount), 1900.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price), self.option_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(self.position_context.max_loss.amount,
                         self.option_order.price * self.option_order.quantity
                         * self.contract_right * -1)
        self.assertEqual(float(self.position_context.max_loss.amount), -190.00)
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


class TestContextNakedCall(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='CALL',
            side='SELL',
            quantity=-4,
            strike=100,
            price=2.9
        )

        self.contract_right = 100
        self.price_multiply = 10

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.naked_call = ContextNakedCall(
            filled_orders=filled_orders
        )
        self.position_context = self.naked_call.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

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
                         self.option_order.strike + self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 102.9)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price),
                         self.option_order.strike + self.option_order.price)
        self.assertEqual(float(self.position_context.start_profit.price), 102.9)
        self.assertEqual(self.position_context.start_profit.condition, '<')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price),
                         self.option_order.strike + self.option_order.price)
        self.assertEqual(float(self.position_context.start_loss.price), 102.9)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price), self.option_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '<=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount),
                         self.option_order.price * self.option_order.quantity
                         * self.contract_right * -1)
        self.assertEqual(float(self.position_context.max_profit.amount), 1160.00)

        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price),
                         self.option_order.strike + (self.option_order.price * self.price_multiply))
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertFalse(self.position_context.max_loss.limit)
        self.assertEqual(float(self.position_context.max_loss.amount),
                         self.option_order.price * self.option_order.quantity
                         * self.price_multiply * self.contract_right)
        self.assertEqual(float(self.position_context.max_loss.amount), -11600.00)
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


class TestContextLongPut(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='BUY',
            quantity=5,
            strike=58,
            price=3.00
        )

        self.contract_right = 100
        self.price_multiply = 10

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.long_put = ContextLongPut(
            filled_orders=filled_orders
        )
        self.position_context = self.long_put.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

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
                         self.option_order.strike - self.option_order.price)
        self.assertEqual(float(self.position_context.break_even.price), 55.00)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price),
                         self.option_order.strike - self.option_order.price)
        self.assertEqual(float(self.position_context.start_profit.price), 55.00)
        self.assertEqual(self.position_context.start_profit.condition, '<')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price),
                         self.option_order.strike - self.option_order.price)
        self.assertEqual(float(self.position_context.start_loss.price), 55.00)
        self.assertEqual(self.position_context.start_loss.condition, '>')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price),
                         self.option_order.strike - (self.option_order.price * self.price_multiply))
        self.assertEqual(float(self.position_context.max_profit.price), 28.00)
        self.assertEqual(self.position_context.max_profit.condition, '==')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(
            float(self.position_context.max_profit.amount),
            ((float(self.position_context.break_even.price) -
              (self.option_order.strike - (self.option_order.price * self.price_multiply)))
             * self.option_order.quantity * self.contract_right)
        )
        self.assertEqual(float(self.position_context.max_profit.amount), 13500.00)
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price), self.option_order.strike)
        self.assertEqual(self.position_context.max_loss.condition, '>=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(self.position_context.max_loss.amount,
                         self.option_order.price * self.option_order.quantity
                         * self.contract_right * -1)
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


class TestContextNakedPut(TestUnitSetUpDB):
    def setUp(self):
        TestUnitSetUpDB.setUp(self)

        self.option_order = create_filled_order(
            trade_summary=self.trade_summary,
            underlying=self.underlying,
            spread='SINGLE',
            contract='PUT',
            side='SELL',
            quantity=-9,
            strike=32,
            price=1.70
        )

        self.contract_right = 100
        self.price_multiply = 10

        filled_orders = FilledOrder.objects.filter(underlying=self.underlying).all()

        self.naked_put = ContextNakedPut(
            filled_orders=filled_orders
        )
        self.position_context = self.naked_put.create_context()

    def tearDown(self):
        TestUnitSetUpDB.tearDown(self)

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
                         self.option_order.strike - self.option_order.price)
        self.assertEqual(self.position_context.break_even.condition, '==')
        print self.position_context.break_even

    def test_start_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.start_profit.id)
        self.assertEqual(float(self.position_context.start_profit.price),
                         self.option_order.strike - self.option_order.price)
        self.assertEqual(self.position_context.start_profit.condition, '>')
        print self.position_context.start_profit

    def test_start_loss(self):
        """
        Left side start loss
        """
        self.assertTrue(self.position_context.start_loss.id)
        self.assertEqual(float(self.position_context.start_loss.price),
                         self.option_order.strike - self.option_order.price)
        self.assertEqual(self.position_context.start_loss.condition, '<')
        print self.position_context.start_loss

    def test_max_profit(self):
        """
        Left side start profit
        """
        self.assertTrue(self.position_context.max_profit.id)
        self.assertEqual(float(self.position_context.max_profit.price), self.option_order.strike)
        self.assertEqual(self.position_context.max_profit.condition, '>=')
        self.assertTrue(self.position_context.max_profit.limit)
        self.assertEqual(float(self.position_context.max_profit.amount), 1530.00)
        self.assertEqual(float(self.position_context.max_profit.amount),
                         (self.option_order.price * self.option_order.quantity
                          * self.contract_right * -1))
        print self.position_context.max_profit

    def test_max_loss(self):
        """
        Left side max loss
        """
        self.assertTrue(self.position_context.max_loss.id)
        self.assertEqual(float(self.position_context.max_loss.price), 15.00)
        self.assertEqual(self.position_context.max_loss.condition, '<=')
        self.assertTrue(self.position_context.max_loss.limit)
        self.assertEqual(self.position_context.max_loss.amount, -13770.00)
        self.assertEqual(
            self.position_context.max_loss.amount,
            round((float(self.position_context.break_even.price) -
                   (self.option_order.strike - (self.option_order.price * self.price_multiply)))
                  * self.option_order.quantity * self.contract_right, 2)
        )
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

