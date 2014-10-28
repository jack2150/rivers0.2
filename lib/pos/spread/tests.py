from lib.test import TestSetUp, TestReadyUp
from pms_app.pos_app.models import Underlying, PositionSet
import lib.pos.spread.__spread as spread


class TestSpreads(TestReadyUp):
    def setUp(self):
        TestReadyUp.setUp(self)

        self.ready_all(key=1)

        position = Underlying.objects.all().first()
        pos_set = PositionSet(position)

        # first create spread
        self.sp = spread.Spread(pos_set)

    def test_not_implemented(self):
        """
        Test all not implemented method raise error
        """
        self.assertRaises(NotImplementedError, lambda: self.sp.json())
        self.assertRaises(NotImplementedError, lambda: self.sp.update_status())
        self.assertRaises(NotImplementedError, lambda: self.sp.__unicode__())

    def test_pl_properties(self):
        """
        Test all PL property
        """
        attrs = ['start_profit', 'start_loss', 'max_profit', 'max_loss', 'break_even']
        clss = ['StartProfit', 'StartLoss', 'MaxProfit', 'MaxLoss', 'BreakEven']
        self.assertEqual(type(self.sp.pls), spread.PLS)
        self.assertEqual(type(self.sp.pl), spread.PL)
        for attr, cls in zip(attrs, clss):
            self.assertEqual(type(getattr(self.sp.pls, attr)), list)
            self.assertEqual(type(getattr(self.sp.pls, attr)[0]), getattr(spread, cls))
            self.assertEqual(type(getattr(self.sp.pl, attr)), getattr(spread, cls))

    def test_spread_properties(self):
        """
        Test spread object have all other property
        """
        self.assertEqual(self.sp.name, 'closed')
        self.assertEqual(self.sp.context, 'closed')


class TestStartProfit(TestSetUp):
    def test_start_profit(self):
        """
        Test start profit and start loss that set value into property
        """
        prices = [11.62, 33.8, 240, 24.96]
        conditions = ['>=', '<', '<=', '>']

        for price, condition in zip(prices, conditions):
            start_profit = spread.StartProfit(price, condition)
            print '%s\n' % start_profit

            self.assertEqual(start_profit.price, price)
            self.assertEqual(start_profit.condition, condition)

            self.assertEqual(type(start_profit.price), float)
            self.assertEqual(type(start_profit.condition), str)

            print start_profit.json()


class TestStartLoss(TestSetUp):
    def test_start_loss(self):
        """
        Test start profit and start loss that set value into property
        """
        prices = [11.62, 33.8, 240, 24.96]
        conditions = ['>=', '<', '<=', '>']

        for price, condition in zip(prices, conditions):
            start_loss = spread.StartLoss(price, condition)
            print '%s\n' % start_loss

            self.assertEqual(start_loss.price, price)
            self.assertEqual(start_loss.condition, condition)

            self.assertEqual(type(start_loss.price), float)
            self.assertEqual(type(start_loss.condition), str)

            print start_loss.json()


class TestMaxProfitMaxLoss(TestSetUp):
    def test_max_profit_max_loss(self):
        """
        Test max profit and max loss class
        """
        amount = [12.5, 55.34, 60.28, 27.54]
        limits = [False, True, True, False]
        prices = [11.62, 33.8, 240, 24.96]
        conditions = ['>=', '<', '<=', '>']

        for amount, limit, price, condition in zip(amount, limits, prices, conditions):
            max_profit = spread.MaxProfit(amount, limit, price, condition)
            max_loss = spread.MaxLoss(amount, limit, price, condition)
            print '%s\n%s\n' % (max_profit, max_loss)

            print max_profit.json()
            print max_loss.json()

            self.assertEqual(max_profit.limit, limit)
            self.assertEqual(max_profit.price, price)
            self.assertEqual(max_profit.condition, condition)

            self.assertEqual(max_loss.limit, limit)
            self.assertEqual(max_loss.price, price)
            self.assertEqual(max_loss.condition, condition)

            if max_profit.limit:
                self.assertEqual(max_profit.amount, amount)
                self.assertEqual(max_loss.amount, amount)
            else:
                self.assertEqual(max_profit.amount, float('inf'))
                self.assertEqual(max_loss.amount, float('inf'))

    def test_max_profit_max_loss_range(self):
        """
        Test max profit and max loss class with range (2 points, double)
        """
        profits_a = [12.5, 55.34, 60.28, 27.54]
        profits_b = [10.75, 50.9, 72.8, 33.69]

        limits_a = [False, True, True, False]
        limits_b = [False, True, False, True]

        prices_a = [11.62, 33.8, 240, 24.96]
        prices_b = [18.62, 41.8, 224.5, 30.8]

        conditions_a = ['>=', '<', '<=', '>']
        conditions_b = ['<=', '>', '>', '<=']

        range_a = zip(profits_a, limits_a, prices_a, conditions_a)
        range_b = zip(profits_b, limits_b, prices_b, conditions_b)

        for a, b in zip(range_a, range_b):
            max_profit_a = spread.MaxProfit(*a)
            max_profit_b = spread.MaxProfit(*b)

            max_loss_a = spread.MaxLoss(*a)
            max_loss_b = spread.MaxLoss(*b)

            print '%s && %s' % (max_profit_a, max_profit_b)
            print '%s && %s\n' % (max_loss_a, max_loss_b)


class TestBreakEven(TestSetUp):
    def test_break_even_single(self):
        """
        Test break even class with single and range (double)
        """
        prices = [11.62, 33.8, 240, 24.96]
        conditions = ['==', '==', '<=', '=>']

        for price, condition in zip(prices, conditions):
            break_even = spread.BreakEven(price, condition)

            print '%s' % break_even

            print break_even.json()

            self.assertEqual(break_even.price, price)
            self.assertEqual(break_even.condition, condition)

    def test_break_even_double(self):
        prices_a = [11.62, 33.8, 240, 24.96]
        prices_b = [18.62, 41.8, 224.5, 30.8]

        conditions_a = ['>=', '<', '<=', '>']
        conditions_b = ['<=', '>', '>', '<=']

        range_a = zip(prices_a, conditions_a)
        range_b = zip(prices_b, conditions_b)

        print ''

        for a, b in zip(range_a, range_b):
            break_even_a = spread.BreakEven(*a)
            break_even_b = spread.BreakEven(*b)

            print '%s && %s' % (break_even_a, break_even_b)
