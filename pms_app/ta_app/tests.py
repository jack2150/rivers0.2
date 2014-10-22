from datetime import datetime
from pprint import pprint
from django.utils.timezone import utc
from lib.test import TestSetUp
from pms_app.ta_app import models


class TestWorkingOrder(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-09-19'
        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)

        self.items = {
            'status': 'WORKING', 'pos_effect': 'AUTO', 'quantity': -100, 'symbol': 'FB',
            'contract': 'STOCK', 'order': 'LMT', 'time_placed': use_dt, 'spread': 'STOCK',
            'expire_date': '', 'strike': 0.0, 'tif': 'GTC', 'mark': 74.5, 'price': 82.0,
            'side': 'SELL'
        }

        self.working_order = models.WorkingOrder(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.working_order.save()

        print 'Trade activity saved!'
        print 'pos id: %d' % self.working_order.id

        self.assertTrue(self.working_order.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'
        pprint(eval(self.working_order.__unicode__()))

        json = self.working_order.__unicode__()
        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)
            self.assertIn(str(item), json)


class TestFilledOrder(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-09-19'
        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)
        self.items = {
            'pos_effect': 'AUTO', 'exec_time': use_dt, 'net_price': 1.05, 'symbol': 'GOOG',
            'contract': 'PUT', 'side': 'BUY', 'price': 10.8, 'spread': 'VERTICAL',
            'expire_date': 'SEP 14', 'strike': 582.5, 'order': 'MKT', 'quantity': 1
        }

        self.filled_order = models.FilledOrder(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.filled_order.save()

        print 'Trade activity saved!'
        print 'pos id: %d' % self.filled_order.id

        self.assertTrue(self.filled_order.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'
        pprint(eval(self.filled_order.__unicode__()))

        json = self.filled_order.__unicode__()
        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)
            self.assertIn(str(item), json)


class TestCancelledOrder(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-09-19'
        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)
        self.items = {
            'status': 'CANCELED', 'pos_effect': 'AUTO', 'time_cancelled': use_dt,
            'price': 82.0, 'contract': 'STOCK', 'side': 'SELL', 'symbol': 'FB',
            'spread': 'STOCK', 'expire_date': '', 'strike': 0.0, 'tif': 'DAY',
            'order': 'LMT', 'quantity': -100
        }

        self.cancelled_order = models.CancelledOrder(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.cancelled_order.save()

        print 'Trade activity saved!'
        print 'pos id: %d' % self.cancelled_order.id

        self.assertTrue(self.cancelled_order.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'
        pprint(eval(self.cancelled_order.__unicode__()))

        json = self.cancelled_order.__unicode__()
        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)
            self.assertIn(str(item), json)


class TestRollingStrategy(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-09-19'
        self.items = {
            'status': 'WAIT TRG', 'right': 100, 'strike_price': 77.5, 'days_begin': 2.0, 'new_expire_date': 'NOV4 14',
            'symbol': 'FB', 'ex_month': 'NOV', 'call_by': 'Strike +1 ATM', 'contract': 'CALL', 'order_price': 'AUTO',
            'ex_year': 14, 'move_to_market_time_start': '11:00:00', 'active_time_start': '08:45:00',
            'active_time_end': '09:00:00', 'side': -1, 'move_to_market_time_end': '14:45:00'
        }

        self.rolling_strategy = models.RollingStrategy(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.rolling_strategy.save()

        print 'Trade activity saved!'
        print 'pos id: %d' % self.rolling_strategy.id

        self.assertTrue(self.rolling_strategy.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'
        pprint(eval(self.rolling_strategy.__unicode__()))

        json = self.rolling_strategy.__unicode__()
        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)
            self.assertIn(str(item), json)