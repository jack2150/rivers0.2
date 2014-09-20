# perfect...
from lib.test import TestReadyUp
from pms_app.pos_app.models import Position, PositionSet
import lib.pos.spread.hedge as hedge


class TestHedgeContext(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=2)

        position = Position.objects.first()
        self.pos_set = PositionSet(position)

        self.hedge_context = hedge.HedgeContext(self.pos_set)

        self.set_prices = [12.5, 20.7, 33.94, 8.71, 114.81]
        self.set_conditions = ['>', '<', '==', '<=', '>=']
        self.test_prices = [13.9, 22.67, 33.94, 7.66, 100.88]

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.hedge_context.json()[:80] + '...\n'

        self.assertTrue(eval(self.hedge_context.json()))
        self.assertEqual(type(self.hedge_context.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.hedge_context.__unicode__()[:80] + '...\n'

        self.assertEqual(type(self.hedge_context.__unicode__()), str)
        self.assertIn('Position', self.hedge_context.__unicode__())

    def test_property(self):
        """
        Test all property inside class
        """
        # check models data exist
        print 'position id: %d' % self.hedge_context.pos_set.instrument.id
        print 'instrument id: %d' % self.hedge_context.pos_set.position.id
        print 'stock id: %d' % self.hedge_context.pos_set.stock.id
        print 'option id: %d\n' % self.hedge_context.pos_set.option.id

        self.assertTrue(self.hedge_context.pos_set.position.id)
        self.assertTrue(self.hedge_context.pos_set.stock.id)
        self.assertTrue(self.hedge_context.pos_set.instrument.id)
        self.assertEqual(self.hedge_context.pos_set.options.count(), 1)
        self.assertTrue(self.hedge_context.pos_set.option.id)

        # check pls is removed
        self.assertRaises(lambda: self.hedge_context.pls)

    def test_is_profit(self):
        """
        Test is profit method
        """
        expect_results = [True, False, True, True, False]
        zipped = zip(self.set_prices, self.set_conditions, self.test_prices, expect_results)
        for set_price, condition, test_price, expect_result in zipped:
            self.hedge_context.pl.start_profit.price = set_price
            self.hedge_context.pl.start_profit.condition = condition

            result = self.hedge_context.is_profit(test_price)

            print 'price: %.2f, condition: %s' % (set_price, condition)
            print 'test: %.2f, result: %s\n' % (test_price, result)

            self.assertEqual(result, expect_result)
            self.assertEqual(type(result), bool)

    def test_is_loss(self):
        """
        Test is loss method
        """
        expect_results = [True, False, True, True, False]
        zipped = zip(self.set_prices, self.set_conditions, self.test_prices, expect_results)
        for set_price, condition, test_price, expect_result in zipped:
            self.hedge_context.pl.start_loss.price = set_price
            self.hedge_context.pl.start_loss.condition = condition

            result = self.hedge_context.is_loss(test_price)

            print 'price: %.2f, condition: %s' % (set_price, condition)
            print 'test: %.2f, result: %s\n' % (test_price, result)

            self.assertEqual(result, expect_result)
            self.assertEqual(type(result), bool)

    def test_is_even(self):
        """
        Test is even method
        """
        expect_results = [False, False, True, False, False]
        zipped = zip(self.set_prices, self.set_conditions, self.test_prices, expect_results)
        for set_price, _, test_price, expect_result in zipped:
            self.hedge_context.pl.break_even.price = set_price
            self.hedge_context.pl.break_even.condition = '=='

            result = self.hedge_context.is_even(test_price)

            print 'price: %.2f, condition: %s' % (set_price, '==')
            print 'test: %.2f, result: %s\n' % (test_price, result)

            self.assertEqual(result, expect_result)
            self.assertEqual(type(result), bool)

    def test_is_max_profit(self):
        """
        Test is max profit method
        """
        expect_results = [True, False, True, True, False]
        zipped = zip(self.set_prices, self.set_conditions, self.test_prices, expect_results)
        for set_price, condition, test_price, expect_result in zipped:
            self.hedge_context.pl.max_profit.price = set_price
            self.hedge_context.pl.max_profit.condition = condition

            result = self.hedge_context.is_max_profit(test_price)

            print 'price: %.2f, condition: %s' % (set_price, condition)
            print 'test: %.2f, result: %s\n' % (test_price, result)

            self.assertEqual(result, expect_result)
            self.assertEqual(type(result), bool)

    def test_is_max_loss(self):
        """
        Test is max loss
        """
        expect_results = [True, False, True, True, False]
        zipped = zip(self.set_prices, self.set_conditions, self.test_prices, expect_results)
        for set_price, condition, test_price, expect_result in zipped:
            self.hedge_context.pl.max_loss.price = set_price
            self.hedge_context.pl.max_loss.condition = condition

            result = self.hedge_context.is_max_loss(test_price)

            print 'price: %.2f, condition: %s' % (set_price, condition)
            print 'test: %.2f, result: %s\n' % (test_price, result)

            self.assertEqual(result, expect_result)
            self.assertEqual(type(result), bool)

    def test_update_status(self):
        """
        Test set status int
        """
        attrs = ['is_even', 'is_max_profit', 'is_profit', 'is_max_loss', 'is_loss']

        for attr in attrs:
            # set method into return true
            setattr(self.hedge_context, attr, lambda price: True)

            status = self.hedge_context.status

            print 'attr: %s, status: %s' % (attr, status)

            # test status in list
            self.assertIn(status, ['even', 'max_profit', 'profit', 'max_loss', 'loss'])

            # set method into return false
            setattr(self.hedge_context, attr, lambda price: False)


class TestCoveredCall(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=2)

        position = Position.objects.get(symbol='AAPL')
        self.pos_set = PositionSet(position)

        self.covered_call = hedge.CoveredCall(self.pos_set)

        self.stock_price = float(self.covered_call.pos_set.stock.trade_price)
        self.stock_quantity = float(self.covered_call.pos_set.stock.quantity)
        self.option_price = float(self.covered_call.pos_set.option.trade_price)
        self.option_strike = float(self.covered_call.pos_set.option.strike_price)

    def test_property(self):
        """
        Test covered call property
        """
        print 'name: %s' % self.covered_call.name
        self.assertEqual(self.covered_call.name, 'covered_call')

    def test_calc_break_even(self):
        """
        Test calc break even return correct value
        """
        calc_result = self.covered_call.calc_break_even()

        print 'break even: %.2f' % calc_result

        expect_result = self.stock_price - self.option_price

        print 'stock_price - option_price = %.2f - %.2f = %s' % (
            self.stock_price, self.option_price, expect_result
        )

        self.assertEqual(calc_result, 92.97)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_profit(self):
        """
        Test calc max profit
        """
        calc_result = self.covered_call.calc_max_profit()

        print 'max profit: %.2f' % calc_result

        expect_result = (self.option_price + self.option_strike
                         - self.stock_price) * self.stock_quantity

        print '(option_price + strike_price - stock_price) * stock_quantity'
        print '(%.2f + %.2f - %.2f) * %d = %s' % (
            self.option_price, self.option_strike, self.stock_price,
            self.stock_quantity, expect_result
        )

        self.assertEqual(calc_result, 453.0)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_loss(self):
        """
        Test calc max profit
        """
        calc_result = self.covered_call.calc_max_loss()

        print 'max loss: %.2f' % calc_result

        expect_result = (self.stock_price - self.option_price) * self.stock_quantity

        print '(stock_price - option_price) * stock_quantity'
        print '(%.2f - %.2f) * %d = %s' % (
            self.stock_price, self.option_price,
            self.stock_quantity, expect_result
        )

        self.assertEqual(calc_result, 9297.0)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_pl_break_even(self):
        """
        Test pl break even property
        """
        print 'price: %.2f' % self.covered_call.pl.break_even.price
        print 'condition: %s' % self.covered_call.pl.break_even.condition

        self.assertEqual(type(self.covered_call.pl.break_even.price), float)
        self.assertEqual(self.covered_call.pl.break_even.condition, '==')

    def test_pl_start_profit(self):
        """
        Test pl start profit property
        """
        print 'price: %.2f' % self.covered_call.pl.start_profit.price
        print 'condition: %s' % self.covered_call.pl.start_profit.condition

        self.assertEqual(type(self.covered_call.pl.start_profit.price), float)
        self.assertEqual(self.covered_call.pl.start_profit.condition, '>')

    def test_pl_start_loss(self):
        """
        Test pl start loss property
        """
        print 'price: %.2f' % self.covered_call.pl.start_loss.price
        print 'condition: %s' % self.covered_call.pl.start_loss.condition

        self.assertEqual(type(self.covered_call.pl.start_loss.price), float)
        self.assertEqual(self.covered_call.pl.start_loss.condition, '<')

    def test_pl_max_profit(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.covered_call.pl.max_profit.amount
        print 'limit: %s' % self.covered_call.pl.max_profit.limit
        print 'price: %.2f' % self.covered_call.pl.max_profit.price
        print 'condition: %s' % self.covered_call.pl.max_profit.condition

        self.assertEqual(type(self.covered_call.pl.max_profit.amount), float)
        self.assertEqual(type(self.covered_call.pl.max_profit.limit), bool)
        self.assertEqual(type(self.covered_call.pl.max_profit.price), float)
        self.assertEqual(self.covered_call.pl.max_profit.condition, '>=')

    def test_pl_max_loss(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.covered_call.pl.max_loss.amount
        print 'limit: %s' % self.covered_call.pl.max_loss.limit
        print 'price: %.2f' % self.covered_call.pl.max_loss.price
        print 'condition: %s' % self.covered_call.pl.max_loss.condition

        self.assertEqual(type(self.covered_call.pl.max_loss.amount), float)
        self.assertEqual(type(self.covered_call.pl.max_loss.limit), bool)
        self.assertEqual(type(self.covered_call.pl.max_loss.price), float)
        self.assertEqual(self.covered_call.pl.max_loss.condition, '==')

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.covered_call.json()[:80] + '...\n'

        self.assertTrue(eval(self.covered_call.json()))
        self.assertEqual(type(self.covered_call.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.covered_call

        self.assertEqual(type(self.covered_call.__unicode__()), str)
        self.assertIn('Position', self.covered_call.__unicode__())


class TestProtectivePut(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=2)

        position = Position.objects.get(symbol='DDD')
        self.pos_set = PositionSet(position)

        self.protective_put = hedge.ProtectivePut(self.pos_set)

        self.stock_price = float(self.protective_put.pos_set.stock.trade_price)
        self.stock_quantity = float(self.protective_put.pos_set.stock.quantity)
        self.option_price = float(self.protective_put.pos_set.option.trade_price)
        self.option_strike = float(self.protective_put.pos_set.option.strike_price)

    def test_property(self):
        """
        Test covered call property
        """
        print 'name: %s' % self.protective_put.name
        self.assertEqual(self.protective_put.name, 'protective_put')

    def test_calc_break_even(self):
        """
        Test calc break even return correct value
        """
        calc_result = self.protective_put.calc_break_even()

        print 'break even: %.2f' % calc_result

        expect_result = self.stock_price + self.option_price

        print 'stock_price + option_price = %.2f + %.2f = %s' % (
            self.stock_price, self.option_price, expect_result
        )

        self.assertEqual(calc_result, 52.46)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_loss(self):
        """
        Test calc max profit
        """
        calc_result = self.protective_put.calc_max_loss()

        print 'max loss: %.2f' % calc_result

        expect_result = (self.stock_price + self.option_price
                         - self.option_strike) * self.stock_quantity

        print '(stock_price + option_price - option_strike) * stock_quantity'
        print '(%.2f + %.2f - %.2f) * %d = %s' % (
            self.stock_price, self.option_price, self.option_strike,
            self.stock_quantity, expect_result
        )

        self.assertEqual(calc_result, 446.0)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_pl_break_even(self):
        """
        Test pl break even property
        """
        print 'price: %.2f' % self.protective_put.pl.break_even.price
        print 'condition: %s' % self.protective_put.pl.break_even.condition

        self.assertEqual(type(self.protective_put.pl.break_even.price), float)
        self.assertEqual(self.protective_put.pl.break_even.condition, '==')

    def test_pl_start_profit(self):
        """
        Test pl start profit property
        """
        print 'price: %.2f' % self.protective_put.pl.start_profit.price
        print 'condition: %s' % self.protective_put.pl.start_profit.condition

        self.assertEqual(type(self.protective_put.pl.start_profit.price), float)
        self.assertEqual(self.protective_put.pl.start_profit.condition, '>')

    def test_pl_start_loss(self):
        """
        Test pl start loss property
        """
        print 'price: %.2f' % self.protective_put.pl.start_loss.price
        print 'condition: %s' % self.protective_put.pl.start_loss.condition

        self.assertEqual(type(self.protective_put.pl.start_loss.price), float)
        self.assertEqual(self.protective_put.pl.start_loss.condition, '<')

    def test_pl_max_profit(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.protective_put.pl.max_profit.amount
        print 'limit: %s' % self.protective_put.pl.max_profit.limit
        print 'price: %.2f' % self.protective_put.pl.max_profit.price
        print 'condition: %s' % self.protective_put.pl.max_profit.condition

        self.assertEqual(self.protective_put.pl.max_profit.amount, float('inf'))
        self.assertEqual(type(self.protective_put.pl.max_profit.amount), float)
        self.assertEqual(type(self.protective_put.pl.max_profit.limit), bool)
        self.assertEqual(type(self.protective_put.pl.max_profit.price), float)
        self.assertEqual(self.protective_put.pl.max_profit.condition, '==')

    def test_pl_max_loss(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.protective_put.pl.max_loss.amount
        print 'limit: %s' % self.protective_put.pl.max_loss.limit
        print 'price: %.2f' % self.protective_put.pl.max_loss.price
        print 'condition: %s' % self.protective_put.pl.max_loss.condition

        self.assertEqual(type(self.protective_put.pl.max_loss.amount), float)
        self.assertEqual(type(self.protective_put.pl.max_loss.limit), bool)
        self.assertEqual(type(self.protective_put.pl.max_loss.price), float)
        self.assertEqual(self.protective_put.pl.max_loss.condition, '<=')

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.protective_put.json()[:80] + '...\n'

        self.assertTrue(eval(self.protective_put.json()))
        self.assertEqual(type(self.protective_put.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.protective_put

        self.assertEqual(type(self.protective_put.__unicode__()), str)
        self.assertIn('Position', self.protective_put.__unicode__())


class TestCoveredPut(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)
        self.ready_all(key=2)

        position = Position.objects.get(symbol='C')
        self.pos_set = PositionSet(position)

        self.covered_put = hedge.CoveredPut(self.pos_set)

        self.stock_price = float(self.covered_put.pos_set.stock.trade_price)
        self.stock_quantity = float(self.covered_put.pos_set.stock.quantity)
        self.option_price = float(self.covered_put.pos_set.option.trade_price)
        self.option_strike = float(self.covered_put.pos_set.option.strike_price)

    def test_property(self):
        """
        Test covered call property
        """
        print 'name: %s' % self.covered_put.name
        self.assertEqual(self.covered_put.name, 'covered_put')

    def test_calc_break_even(self):
        """
        Test calc break even return correct value
        """
        calc_result = self.covered_put.calc_break_even()

        print 'break even: %.2f' % calc_result

        expect_result = self.stock_price + self.option_price

        print 'stock_price + option_price = %.2f + %.2f = %s' % (
            self.stock_price, self.option_price, expect_result
        )

        self.assertEqual(calc_result, 49.43)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_profit(self):
        """
        Test calc max profit
        """
        calc_result = self.covered_put.calc_max_profit()

        print 'max profit: %.2f' % calc_result

        expect_result = (self.option_strike - self.option_price
                         - self.stock_price) * self.stock_quantity

        print '(strike_price - option_price - stock_price) * stock_quantity'
        print '(%.2f - %.2f - %.2f) * %d = %s' % (
            self.option_strike, self.option_price, self.stock_price,
            self.stock_quantity, expect_result
        )

        self.assertEqual(calc_result, 143.0)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_pl_break_even(self):
        """
        Test pl break even property
        """
        print 'price: %.2f' % self.covered_put.pl.break_even.price
        print 'condition: %s' % self.covered_put.pl.break_even.condition

        self.assertEqual(type(self.covered_put.pl.break_even.price), float)
        self.assertEqual(self.covered_put.pl.break_even.condition, '==')

    def test_pl_start_profit(self):
        """
        Test pl start profit property
        """
        print 'price: %.2f' % self.covered_put.pl.start_profit.price
        print 'condition: %s' % self.covered_put.pl.start_profit.condition

        self.assertEqual(type(self.covered_put.pl.start_profit.price), float)
        self.assertEqual(self.covered_put.pl.start_profit.condition, '<')

    def test_pl_start_loss(self):
        """
        Test pl start loss property
        """
        print 'price: %.2f' % self.covered_put.pl.start_loss.price
        print 'condition: %s' % self.covered_put.pl.start_loss.condition

        self.assertEqual(type(self.covered_put.pl.start_loss.price), float)
        self.assertEqual(self.covered_put.pl.start_loss.condition, '>')

    def test_pl_max_profit(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.covered_put.pl.max_profit.amount
        print 'limit: %s' % self.covered_put.pl.max_profit.limit
        print 'price: %.2f' % self.covered_put.pl.max_profit.price
        print 'condition: %s' % self.covered_put.pl.max_profit.condition

        self.assertEqual(type(self.covered_put.pl.max_profit.amount), float)
        self.assertEqual(type(self.covered_put.pl.max_profit.limit), bool)
        self.assertEqual(type(self.covered_put.pl.max_profit.price), float)
        self.assertEqual(self.covered_put.pl.max_profit.condition, '<=')

    def test_pl_max_loss(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.covered_put.pl.max_loss.amount
        print 'limit: %s' % self.covered_put.pl.max_loss.limit
        print 'price: %.2f' % self.covered_put.pl.max_loss.price
        print 'condition: %s' % self.covered_put.pl.max_loss.condition

        self.assertEqual(type(self.covered_put.pl.max_loss.amount), float)
        self.assertEqual(type(self.covered_put.pl.max_loss.limit), bool)
        self.assertEqual(type(self.covered_put.pl.max_loss.price), float)
        self.assertEqual(self.covered_put.pl.max_loss.price, float('inf'))
        self.assertEqual(self.covered_put.pl.max_loss.condition, '==')

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.covered_put.json()[:80] + '...\n'

        self.assertTrue(eval(self.covered_put.json()))
        self.assertEqual(type(self.covered_put.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.covered_put

        self.assertEqual(type(self.covered_put.__unicode__()), str)
        self.assertIn('Position', self.covered_put.__unicode__())


class TestProtectiveCall(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)

        self.ready_all(key=2)
        position = Position.objects.get(symbol='BAC')
        self.pos_set = PositionSet(position)

        self.protective_call = hedge.ProtectiveCall(self.pos_set)

        self.stock_price = float(self.protective_call.pos_set.stock.trade_price)
        self.stock_quantity = float(self.protective_call.pos_set.stock.quantity)
        self.option_price = float(self.protective_call.pos_set.option.trade_price)
        self.option_strike = float(self.protective_call.pos_set.option.strike_price)

    def test_property(self):
        """
        Test covered call property
        """
        print 'name: %s' % self.protective_call.name
        self.assertEqual(self.protective_call.name, 'protective_call')

    def test_calc_break_even(self):
        """
        Test calc break even return correct value
        """
        calc_result = self.protective_call.calc_break_even()

        print 'break even: %.2f' % calc_result

        expect_result = self.stock_price - self.option_price

        print 'stock_price - option_price = %.2f + %.2f = %s' % (
            self.stock_price, self.option_price, expect_result
        )

        self.assertEqual(calc_result, 14.65)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_profit(self):
        """
        Test calc max profit
        """
        calc_result = self.protective_call.calc_max_profit()

        print 'max profit: %.2f' % calc_result

        expect_result = (self.option_price - self.stock_price) * self.stock_quantity

        print '(option_price - stock_price) * stock_quantity'
        print '(%.2f - %.2f) * %d = %s' % (
            self.option_strike, self.option_price,
            self.stock_quantity, expect_result
        )

        self.assertEqual(calc_result, 1465.0)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_calc_max_loss(self):
        """
        Test calc max profit
        """
        calc_result = self.protective_call.calc_max_loss()

        print 'max loss: %.2f' % calc_result

        expect_result = (self.stock_price - self.option_price
                         - self.option_strike) * self.stock_quantity
        print '(stock_price - option_price - option_strike) * stock_quantity'
        print '(%.2f - %.2f - %.2f) * %d = %s' % (
            self.stock_price, self.option_price, self.option_strike,
            self.stock_quantity, expect_result
        )

        self.assertEqual(calc_result, 35.0)
        self.assertEqual(calc_result, round(expect_result, 2))
        self.assertEqual(type(calc_result), float)

    def test_pl_break_even(self):
        """
        Test pl break even property
        """
        print 'price: %.2f' % self.protective_call.pl.break_even.price
        print 'condition: %s' % self.protective_call.pl.break_even.condition

        self.assertEqual(type(self.protective_call.pl.break_even.price), float)
        self.assertEqual(self.protective_call.pl.break_even.condition, '==')

    def test_pl_start_profit(self):
        """
        Test pl start profit property
        """
        print 'price: %.2f' % self.protective_call.pl.start_profit.price
        print 'condition: %s' % self.protective_call.pl.start_profit.condition

        self.assertEqual(type(self.protective_call.pl.start_profit.price), float)
        self.assertEqual(self.protective_call.pl.start_profit.condition, '<')

    def test_pl_start_loss(self):
        """
        Test pl start loss property
        """
        print 'price: %.2f' % self.protective_call.pl.start_loss.price
        print 'condition: %s' % self.protective_call.pl.start_loss.condition

        self.assertEqual(type(self.protective_call.pl.start_loss.price), float)
        self.assertEqual(self.protective_call.pl.start_loss.condition, '>')

    def test_pl_max_profit(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.protective_call.pl.max_profit.amount
        print 'limit: %s' % self.protective_call.pl.max_profit.limit
        print 'price: %.2f' % self.protective_call.pl.max_profit.price
        print 'condition: %s' % self.protective_call.pl.max_profit.condition

        self.assertEqual(type(self.protective_call.pl.max_profit.amount), float)
        self.assertEqual(type(self.protective_call.pl.max_profit.limit), bool)
        self.assertEqual(type(self.protective_call.pl.max_profit.price), float)
        self.assertEqual(self.protective_call.pl.max_profit.price, 0.0)
        self.assertEqual(self.protective_call.pl.max_profit.condition, '==')

    def test_pl_max_loss(self):
        """
        Test pl max profit property
        """
        print 'amount: %.2f' % self.protective_call.pl.max_loss.amount
        print 'limit: %s' % self.protective_call.pl.max_loss.limit
        print 'price: %.2f' % self.protective_call.pl.max_loss.price
        print 'condition: %s' % self.protective_call.pl.max_loss.condition

        self.assertEqual(type(self.protective_call.pl.max_loss.amount), float)
        self.assertEqual(type(self.protective_call.pl.max_loss.limit), bool)
        self.assertEqual(type(self.protective_call.pl.max_loss.price), float)
        self.assertEqual(self.protective_call.pl.max_loss.condition, '>=')

    def test_json(self):
        """
        Test json output is working fine
        """
        print 'json:'
        print self.protective_call.json()[:80] + '...\n'

        self.assertTrue(eval(self.protective_call.json()))
        self.assertEqual(type(self.protective_call.json()), str)

    def test_unicode_output(self):
        """
        Test unicode output
        """
        # check str output and json
        print 'output:'
        print self.protective_call

        self.assertEqual(type(self.protective_call.__unicode__()), str)
        self.assertIn('Position', self.protective_call.__unicode__())