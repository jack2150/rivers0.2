from datetime import datetime
from pprint import pprint
from django.utils.timezone import utc
from lib.test import TestSetUp
from pms_app.acc_app import models


class TestCashBalance(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.items = {
            'description': 'SOLD -1 VERTICAL FXI 100 AUG 14 40/38.5 PUT @.59', 'commissions': -3.0,
            'time': '02:49:35', 'contract': 'TRD', 'ref_no': 798680668, 'amount': 59.0, 'fees': -0.07,
            'date': '2014-07-24', 'balance': 956.94
        }

        self.cash_balance = models.CashBalance(**self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.cash_balance.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.cash_balance.id

        self.assertTrue(self.cash_balance.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'
        pprint(eval(self.cash_balance.__unicode__()))

        json = self.cash_balance.__unicode__()
        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)
            self.assertIn(str(item), json)


class TestProfitsLosses(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-07-24'
        self.items = {
            'pl_pct': 0.0, 'description': 'GOLDMAN SACHS GROUP INC COM', 'pl_open': 0.0,
            'margin_req': 0.0, 'symbol': 'GS', 'pl_day': 0.0, 'pl_ytd': -292.0
        }

        self.profits_losses = models.ProfitsLosses(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.profits_losses.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.profits_losses.id

        self.assertTrue(self.profits_losses.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'

        pprint(eval(self.profits_losses.__unicode__()))

        json = self.profits_losses.__unicode__()
        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)
            self.assertIn(str(item), json)


class TestAccountSummary(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-07-24'
        self.items = {
            'commissions_ytd': 1575.08,
            'futures_commissions_ytd': 0.0,
            'net_liquid_value': 3693.94,
            'option_buying_power': 2206.94,
            'stock_buying_power': 5063.58
        }

        self.account_summary = models.AccountSummary(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.account_summary.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.account_summary.id

        self.assertTrue(self.account_summary.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'

        pprint(eval(self.account_summary.__unicode__()))

        json = self.account_summary.__unicode__()
        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)
            self.assertIn(str(item), json)


class TestOrderHistory(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-07-24'
        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)
        self.items ={
            'status': 'CANCELED', 'pos_effect': 'TO CLOSE', 'price': 0.95, 'contract': 'PUT',
            'side': 'BUY', 'symbol': 'FB', 'time_placed': use_dt, 'spread': 'VERTICAL',
            'expire_date': 'JUL4 14', 'strike': 67.0, 'tif': 'GTC', 'order': 'MKT', 'quantity': 1
        }

        self.order_history = models.OrderHistory(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.order_history.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.order_history.id

        self.assertTrue(self.order_history.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'

        json = self.order_history.__unicode__()
        pprint(eval(json))

        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)

            if key == 'time_placed':
                self.assertEqual(type(item), datetime)
            else:
                self.assertIn(str(item), json)


class TestTradeHistory(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-07-24'
        use_dt = datetime(2014, 9, 28, 17, 57, 31, 114000, tzinfo=utc)
        self.items = {
            'pos_effect': 'TO CLOSE', 'order_type': 'LMT', 'net_price': 0.96, 'side': 'SELL',
            'contract': 'CALL', 'symbol': 'USO', 'spread': 'VERTICAL', 'expire_date': 'JUL4 14',
            'execute_time': use_dt, 'strike': 37.5, 'price': 0.57, 'quantity': -3
        }

        self.trade_history = models.TradeHistory(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.trade_history.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.trade_history.id

        self.assertTrue(self.trade_history.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'

        json = self.trade_history.__unicode__()
        pprint(eval(json))

        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)

            if key == 'execute_time':
                self.assertEqual(type(item), datetime)
            else:
                self.assertIn(str(item), json)


class TestEquities(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-07-24'
        self.items = {
            'symbol': 'TZA', 'trade_price': 15.12, 'quantity': 200,
            'description': 'DIREXION SHARES TRUST DAILY SMALL CAP BEAR 3X SHAR'
        }

        self.equities = models.Equities(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.equities.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.equities.id

        self.assertTrue(self.equities.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'

        json = self.equities.__unicode__()
        pprint(eval(json))

        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)

            self.assertIn(str(item), json)


class TestOptions(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-07-24'
        self.items = {
            'symbol': 'TLT', 'contract': 'PUT', 'option_code': 'TLT140816P113',
            'expire_date': 'AUG 14', 'strike': 113.0, 'trade_price': 0.74, 'quantity': 3
        }

        self.options = models.Options(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.options.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.options.id

        self.assertTrue(self.options.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'

        json = self.options.__unicode__()
        pprint(eval(json))

        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)

            self.assertIn(str(item), json)


class TestFutures(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-07-24'
        self.items = {
            'execute_date': '2014-07-23', 'description': 'Enter Market', 'commissions': 4.95, 'fees': 2.34,
            'contract': 'BUY', 'execute_time': '22:21:27', 'ref_no': 'ABC123456', 'amount': 3130.0,
            'trade_date': '2014-07-23', 'balance': 4000.0
        }

        self.futures = models.Futures(date=self.date, **self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.futures.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.futures.id

        self.assertTrue(self.futures.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'

        json = self.futures.__unicode__()
        pprint(eval(json))

        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)

            self.assertIn(str(item), json)


class TestForex(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.items = {
            'amount_usd': 0.0, 'description': 'Cash balance at the start of the business day 23.07 CST',
            'commissions': 0.0, 'contract': 'BAL', 'ref_no': 0L, 'amount': 0.0, 'time': '13:00:00',
            'date': '2014-07-23', 'balance': 0.0
        }

        self.forex = models.Forex(**self.items)

    def test_save(self):
        """
        Test set dict data into pos
        """
        self.forex.save()

        print 'Account statement saved!'
        print 'pos id: %d' % self.forex.id

        self.assertTrue(self.forex.id)

    def test_json(self):
        """
        Test output json format data
        """
        print 'acc in json:'

        json = self.forex.__unicode__()
        pprint(eval(json))

        self.assertEqual('{', json[0])
        self.assertEqual('}', json[-1])

        for key, item in self.items.items():
            self.assertIn(key, json)

            self.assertIn(str(item), json)