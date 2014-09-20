from lib.test import TestReadyUp
from pms_app.pos_app.models import Position, PositionSet
import lib.pos.spread.leg_one as leg_one


class TestLegOneContext(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=3)

        position = Position.objects.first()
        self.pos_set = PositionSet(position)

        self.leg_one_context = leg_one.LegOneContext(self.pos_set)

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.leg_one_context.json()[:80] + '...\n'

        self.assertTrue(eval(self.leg_one_context.json()))
        self.assertEqual(type(self.leg_one_context.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.leg_one_context.__unicode__()[:80] + '...\n'

        self.assertEqual(type(self.leg_one_context.__unicode__()), str)
        self.assertIn('Position', self.leg_one_context.__unicode__())

    def test_property(self):
        """
        Test all property inside class
        """
        # check models data exist
        print 'position id: %d' % self.leg_one_context.pos_set.instrument.id
        print 'instrument id: %d' % self.leg_one_context.pos_set.position.id
        print 'stock id: %d' % self.leg_one_context.pos_set.stock.id
        print 'option id: %d\n' % self.leg_one_context.pos_set.option.id

        self.assertTrue(self.leg_one_context.pos_set.position.id)
        self.assertTrue(self.leg_one_context.pos_set.stock.id)
        self.assertTrue(self.leg_one_context.pos_set.instrument.id)
        self.assertEqual(self.leg_one_context.pos_set.options.count(), 1)
        self.assertTrue(self.leg_one_context.pos_set.option.id)

        # check pls is removed
        self.assertRaises(lambda: self.leg_one_context.pls)


class TestCallLong(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=3)

        position = Position.objects.get(symbol='AAPL')
        self.pos_set = PositionSet(position)

        self.call_long = leg_one.CallLong(self.pos_set)

        self.option_price = float(self.call_long.pos_set.option.trade_price)
        self.option_strike = float(self.call_long.pos_set.option.strike_price)
        self.option_quantity = float(self.call_long.pos_set.option.quantity)
        self.option_right = int(self.call_long.pos_set.option.right)

    def test_property(self):
        """
        Test covered call property
        """
        print 'name: %s' % self.call_long.name
        self.assertEqual(self.call_long.name, 'long_call')

    def test_calc_break_even(self):
        """
        Test calc break even return correct value
        """
        calc_result = self.call_long.calc_break_even()

        print 'break even: %.2f' % calc_result

        expect_result = self.option_strike + self.option_price

        print 'option_strike + option_price = %.2f + %.2f = %s' % (
            self.option_strike, self.option_price, expect_result
        )

        self.assertEqual(calc_result, 99.86)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_loss(self):
        """
        Test calc max profit
        """
        calc_result = self.call_long.calc_max_loss()

        print 'max loss: %.2f' % calc_result

        expect_result = self.option_price * self.option_quantity * self.option_right

        print 'option_price * option_quantity * option_right'
        print '%.2f * %.2f * %.2f = %.2f' % (
            self.option_price, self.option_quantity,
            self.option_right, expect_result
        )

        self.assertEqual(calc_result, 236.00)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_pl_break_even(self):
        """
        Test pl break even property
        """
        print 'price: %.2f' % self.call_long.pl.break_even.price
        print 'condition: %s' % self.call_long.pl.break_even.condition

        self.assertEqual(type(self.call_long.pl.break_even.price), float)
        self.assertEqual(self.call_long.pl.break_even.condition, '==')

    def test_pl_start_profit(self):
        """
        Test pl start profit property
        """
        print 'price: %.2f' % self.call_long.pl.start_profit.price
        print 'condition: %s' % self.call_long.pl.start_profit.condition

        self.assertEqual(type(self.call_long.pl.start_profit.price), float)
        self.assertEqual(self.call_long.pl.start_profit.condition, '>')

    def test_pl_start_loss(self):
        """
        Test pl start loss property
        """
        print 'price: %.2f' % self.call_long.pl.start_loss.price
        print 'condition: %s' % self.call_long.pl.start_loss.condition

        self.assertEqual(type(self.call_long.pl.start_loss.price), float)
        self.assertEqual(self.call_long.pl.start_loss.condition, '<')

    def test_pl_max_profit(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.call_long.pl.max_profit.amount
        print 'limit: %s' % self.call_long.pl.max_profit.limit
        print 'price: %.2f' % self.call_long.pl.max_profit.price
        print 'condition: %s' % self.call_long.pl.max_profit.condition

        self.assertEqual(self.call_long.pl.max_profit.amount, float('inf'))
        self.assertEqual(type(self.call_long.pl.max_profit.amount), float)
        self.assertEqual(type(self.call_long.pl.max_profit.limit), bool)
        self.assertEqual(type(self.call_long.pl.max_profit.price), float)
        self.assertEqual(self.call_long.pl.max_profit.condition, '==')

    def test_pl_max_loss(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.call_long.pl.max_loss.amount
        print 'limit: %s' % self.call_long.pl.max_loss.limit
        print 'price: %.2f' % self.call_long.pl.max_loss.price
        print 'condition: %s' % self.call_long.pl.max_loss.condition

        self.assertEqual(type(self.call_long.pl.max_loss.amount), float)
        self.assertEqual(type(self.call_long.pl.max_loss.limit), bool)
        self.assertEqual(type(self.call_long.pl.max_loss.price), float)
        self.assertEqual(self.call_long.pl.max_loss.condition, '<=')

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.call_long.json()[:80] + '...\n'

        self.assertTrue(eval(self.call_long.json()))
        self.assertEqual(type(self.call_long.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.call_long

        self.assertEqual(type(self.call_long.__unicode__()), str)
        self.assertIn('Position', self.call_long.__unicode__())


class TestCallNaked(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=3)

        position = Position.objects.get(symbol='FB')
        self.pos_set = PositionSet(position)

        self.call_naked = leg_one.CallNaked(self.pos_set)

        self.option_price = float(self.call_naked.pos_set.option.trade_price)
        self.option_strike = float(self.call_naked.pos_set.option.strike_price)
        self.option_quantity = float(self.call_naked.pos_set.option.quantity)
        self.option_right = int(self.call_naked.pos_set.option.right)

    def test_property(self):
        """
        Test covered call property
        """
        print 'name: %s' % self.call_naked.name
        self.assertEqual(self.call_naked.name, 'naked_call')

    def test_calc_break_even(self):
        """
        Test calc break even return correct value
        """
        calc_result = self.call_naked.calc_break_even()

        print 'break even: %.2f' % calc_result

        expect_result = self.option_strike + self.option_price

        print 'option_strike + option_price = %.2f + %.2f = %s' % (
            self.option_strike, self.option_price, expect_result
        )

        self.assertEqual(calc_result, 76.87)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_profit(self):
        """
        Test calc max profit
        """
        calc_result = self.call_naked.calc_max_profit()

        print 'max profit: %.2f' % calc_result

        expect_result = self.option_price * abs(self.option_quantity) * self.option_right

        print 'option_price * option_quantity * option_right'
        print '%.2f * %.2f * %.2f = %.2f' % (
            self.option_price, self.option_quantity,
            self.option_right, expect_result
        )

        self.assertEqual(calc_result, 187.00)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_pl_break_even(self):
        """
        Test pl break even property
        """
        print 'price: %.2f' % self.call_naked.pl.break_even.price
        print 'condition: %s' % self.call_naked.pl.break_even.condition

        self.assertEqual(type(self.call_naked.pl.break_even.price), float)
        self.assertEqual(self.call_naked.pl.break_even.condition, '==')

    def test_pl_start_profit(self):
        """
        Test pl start profit property
        """
        print 'price: %.2f' % self.call_naked.pl.start_profit.price
        print 'condition: %s' % self.call_naked.pl.start_profit.condition

        self.assertEqual(type(self.call_naked.pl.start_profit.price), float)
        self.assertEqual(self.call_naked.pl.start_profit.condition, '<')

    def test_pl_start_loss(self):
        """
        Test pl start loss property
        """
        print 'price: %.2f' % self.call_naked.pl.start_loss.price
        print 'condition: %s' % self.call_naked.pl.start_loss.condition

        self.assertEqual(type(self.call_naked.pl.start_loss.price), float)
        self.assertEqual(self.call_naked.pl.start_loss.condition, '>')

    def test_pl_max_profit(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.call_naked.pl.max_profit.amount
        print 'limit: %s' % self.call_naked.pl.max_profit.limit
        print 'price: %.2f' % self.call_naked.pl.max_profit.price
        print 'condition: %s' % self.call_naked.pl.max_profit.condition

        self.assertEqual(type(self.call_naked.pl.max_profit.amount), float)
        self.assertEqual(type(self.call_naked.pl.max_profit.limit), bool)
        self.assertEqual(type(self.call_naked.pl.max_profit.price), float)
        self.assertEqual(self.call_naked.pl.max_profit.condition, '<=')

    def test_pl_max_loss(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.call_naked.pl.max_loss.amount
        print 'limit: %s' % self.call_naked.pl.max_loss.limit
        print 'price: %.2f' % self.call_naked.pl.max_loss.price
        print 'condition: %s' % self.call_naked.pl.max_loss.condition

        self.assertEqual(self.call_naked.pl.max_loss.amount, float('inf'))
        self.assertEqual(type(self.call_naked.pl.max_loss.amount), float)
        self.assertEqual(type(self.call_naked.pl.max_loss.limit), bool)
        self.assertEqual(type(self.call_naked.pl.max_loss.price), float)
        self.assertEqual(self.call_naked.pl.max_loss.condition, '==')

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.call_naked.json()[:80] + '...\n'

        self.assertTrue(eval(self.call_naked.json()))
        self.assertEqual(type(self.call_naked.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.call_naked

        self.assertEqual(type(self.call_naked.__unicode__()), str)
        self.assertIn('Position', self.call_naked.__unicode__())


class TestPutLong(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=3)

        position = Position.objects.get(symbol='IBM')
        self.pos_set = PositionSet(position)

        self.put_long = leg_one.PutLong(self.pos_set)

        self.option_price = float(self.put_long.pos_set.option.trade_price)
        self.option_strike = float(self.put_long.pos_set.option.strike_price)
        self.option_quantity = float(self.put_long.pos_set.option.quantity)
        self.option_right = int(self.put_long.pos_set.option.right)

    def test_property(self):
        """
        Test covered call property
        """
        print 'name: %s' % self.put_long.name
        self.assertEqual(self.put_long.name, 'long_put')

    def test_calc_break_even(self):
        """
        Test calc break even return correct value
        """
        calc_result = self.put_long.calc_break_even()

        print 'break even: %.2f' % calc_result

        expect_result = self.option_strike - self.option_price

        print 'option_strike - option_price = %.2f - %.2f = %s' % (
            self.option_strike, self.option_price, expect_result
        )

        self.assertEqual(calc_result, 182.27)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_profit(self):
        """
        Test calc max profit
        """
        calc_result = self.put_long.calc_max_profit()

        print 'max profit: %.2f' % calc_result

        expect_result = ((self.option_strike - self.option_price)
                         * self.option_quantity * self.option_right)

        print '(option_strike - option_price) * option_quantity * option_right'
        print '%.2f - %.2f * %.2f * %.2f = %.2f' % (
            self.option_strike, self.option_price, self.option_quantity,
            self.option_right, expect_result
        )

        self.assertEqual(calc_result, 18227.00)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_loss(self):
        """
        Test calc max profit
        """
        calc_result = self.put_long.calc_max_loss()

        print 'max profit: %.2f' % calc_result

        expect_result = self.option_price * self.option_quantity * self.option_right

        print 'option_price * option_quantity * option_right'
        print '%.2f * %.2f * %.2f = %.2f' % (
            self.option_price, self.option_quantity,
            self.option_right, expect_result
        )

        self.assertEqual(calc_result, 273.00)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_pl_break_even(self):
        """
        Test pl break even property
        """
        print 'price: %.2f' % self.put_long.pl.break_even.price
        print 'condition: %s' % self.put_long.pl.break_even.condition

        self.assertEqual(type(self.put_long.pl.break_even.price), float)
        self.assertEqual(self.put_long.pl.break_even.condition, '==')

    def test_pl_start_profit(self):
        """
        Test pl start profit property
        """
        print 'price: %.2f' % self.put_long.pl.start_profit.price
        print 'condition: %s' % self.put_long.pl.start_profit.condition

        self.assertEqual(type(self.put_long.pl.start_profit.price), float)
        self.assertEqual(self.put_long.pl.start_profit.condition, '<')

    def test_pl_start_loss(self):
        """
        Test pl start loss property
        """
        print 'price: %.2f' % self.put_long.pl.start_loss.price
        print 'condition: %s' % self.put_long.pl.start_loss.condition

        self.assertEqual(type(self.put_long.pl.start_loss.price), float)
        self.assertEqual(self.put_long.pl.start_loss.condition, '>')

    def test_pl_max_profit(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.put_long.pl.max_profit.amount
        print 'limit: %s' % self.put_long.pl.max_profit.limit
        print 'price: %.2f' % self.put_long.pl.max_profit.price
        print 'condition: %s' % self.put_long.pl.max_profit.condition

        self.assertEqual(type(self.put_long.pl.max_profit.amount), float)
        self.assertEqual(type(self.put_long.pl.max_profit.limit), bool)
        self.assertEqual(type(self.put_long.pl.max_profit.price), float)
        self.assertEqual(self.put_long.pl.max_profit.condition, '==')

    def test_pl_max_loss(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.put_long.pl.max_loss.amount
        print 'limit: %s' % self.put_long.pl.max_loss.limit
        print 'price: %.2f' % self.put_long.pl.max_loss.price
        print 'condition: %s' % self.put_long.pl.max_loss.condition

        self.assertEqual(type(self.put_long.pl.max_loss.amount), float)
        self.assertEqual(type(self.put_long.pl.max_loss.limit), bool)
        self.assertEqual(type(self.put_long.pl.max_loss.price), float)
        self.assertEqual(self.put_long.pl.max_loss.condition, '>=')

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.put_long.json()[:80] + '...\n'

        self.assertTrue(eval(self.put_long.json()))
        self.assertEqual(type(self.put_long.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.put_long

        self.assertEqual(type(self.put_long.__unicode__()), str)
        self.assertIn('Position', self.put_long.__unicode__())


class TestPutNaked(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=3)

        position = Position.objects.get(symbol='FSLR')
        self.pos_set = PositionSet(position)

        self.put_naked = leg_one.PutNaked(self.pos_set)

        self.option_price = float(self.put_naked.pos_set.option.trade_price)
        self.option_strike = float(self.put_naked.pos_set.option.strike_price)
        self.option_quantity = float(self.put_naked.pos_set.option.quantity)
        self.option_right = int(self.put_naked.pos_set.option.right)

    def test_property(self):
        """
        Test covered call property
        """
        print 'name: %s' % self.put_naked.name
        self.assertEqual(self.put_naked.name, 'naked_put')

    def test_calc_break_even(self):
        """
        Test calc break even return correct value
        """
        calc_result = self.put_naked.calc_break_even()

        print 'break even: %.2f' % calc_result

        expect_result = self.option_strike - self.option_price

        print 'option_strike - option_price = %.2f - %.2f = %s' % (
            self.option_strike, self.option_price, expect_result
        )

        self.assertEqual(calc_result, 63.09)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_profit(self):
        """
        Test calc max profit
        """
        calc_result = self.put_naked.calc_max_profit()

        print 'max profit: %.2f' % calc_result

        expect_result = self.option_price * abs(self.option_quantity) * self.option_right

        print 'option_price * option_quantity * option_right'
        print '%.2f * %.2f * %.2f = %.2f' % (
            self.option_price, abs(self.option_quantity),
            self.option_right, expect_result
        )

        self.assertEqual(calc_result, 191.00)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_loss(self):
        """
        Test calc max profit
        """
        calc_result = self.put_naked.calc_max_loss()

        print 'max profit: %.2f' % calc_result

        expect_result = ((self.option_strike - self.option_price)
                         * abs(self.option_quantity) * self.option_right)

        print '(option_strike - option_price) * option_quantity * option_right'
        print '%.2f - %.2f * %.2f * %.2f = %.2f' % (
            self.option_strike, self.option_price, self.option_quantity,
            self.option_right, expect_result
        )

        self.assertEqual(calc_result, 6309.00)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_pl_break_even(self):
        """
        Test pl break even property
        """
        print 'price: %.2f' % self.put_naked.pl.break_even.price
        print 'condition: %s' % self.put_naked.pl.break_even.condition

        self.assertEqual(type(self.put_naked.pl.break_even.price), float)
        self.assertEqual(self.put_naked.pl.break_even.condition, '==')

    def test_pl_start_profit(self):
        """
        Test pl start profit property
        """
        print 'price: %.2f' % self.put_naked.pl.start_profit.price
        print 'condition: %s' % self.put_naked.pl.start_profit.condition

        self.assertEqual(type(self.put_naked.pl.start_profit.price), float)
        self.assertEqual(self.put_naked.pl.start_profit.condition, '>')

    def test_pl_start_loss(self):
        """
        Test pl start loss property
        """
        print 'price: %.2f' % self.put_naked.pl.start_loss.price
        print 'condition: %s' % self.put_naked.pl.start_loss.condition

        self.assertEqual(type(self.put_naked.pl.start_loss.price), float)
        self.assertEqual(self.put_naked.pl.start_loss.condition, '<')

    def test_pl_max_profit(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.put_naked.pl.max_profit.amount
        print 'limit: %s' % self.put_naked.pl.max_profit.limit
        print 'price: %.2f' % self.put_naked.pl.max_profit.price
        print 'condition: %s' % self.put_naked.pl.max_profit.condition

        self.assertEqual(type(self.put_naked.pl.max_profit.amount), float)
        self.assertEqual(type(self.put_naked.pl.max_profit.limit), bool)
        self.assertEqual(type(self.put_naked.pl.max_profit.price), float)
        self.assertEqual(self.put_naked.pl.max_profit.condition, '>=')

    def test_pl_max_loss(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.put_naked.pl.max_loss.amount
        print 'limit: %s' % self.put_naked.pl.max_loss.limit
        print 'price: %.2f' % self.put_naked.pl.max_loss.price
        print 'condition: %s' % self.put_naked.pl.max_loss.condition

        self.assertEqual(type(self.put_naked.pl.max_loss.amount), float)
        self.assertEqual(type(self.put_naked.pl.max_loss.limit), bool)
        self.assertEqual(type(self.put_naked.pl.max_loss.price), float)
        self.assertEqual(self.put_naked.pl.max_loss.condition, '<=')

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.put_naked.json()[:80] + '...\n'

        self.assertTrue(eval(self.put_naked.json()))
        self.assertEqual(type(self.put_naked.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.put_naked

        self.assertEqual(type(self.put_naked.__unicode__()), str)
        self.assertIn('Position', self.put_naked.__unicode__())