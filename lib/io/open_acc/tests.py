import os
from pprint import pprint
from lib.test import TestSetUp
from lib.io.open_acc import OpenAcc
from rivers.settings import FILES


class TestOpenAcc(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.fnames = ['2014-07-23-AccountStatement.csv',
                       '2014-07-24-AccountStatement.csv',
                       '2014-07-25-AccountStatement.csv',
                       '2014-07-28-AccountStatement.csv',
                       '2014-07-29-AccountStatement.csv']

        self.fnames[0] = r'C:\Users\Jack\Projects\rivers\pms_app\tests\2014-11-01\2014-11-01-AccountStatement.csv'

        #self.test_file = os.path.join(FILES['account_statement'], self.fnames[0])
        self.test_file = self.fnames[0]
        self.sample_data = open(self.test_file).read()

        self.open_acc = OpenAcc(data=self.sample_data)

    def test_property(self):
        """
        Test property inside class
        """
        properties = ['summary_keys', 'profits_losses_keys', 'options_keys',
                      'trade_history_keys', 'order_history_keys',
                      'forex_keys', 'futures_statements_keys',
                      'holding_future_keys', 'cash_balance_keys']

        for prop in properties:
            print '%s:' % prop
            column = getattr(self.open_acc, prop)

            pprint(column)
            self.assertTrue(len(column))

            print ''

    def test_get_summary_data(self):
        """
        Test get summary data from a list
        """
        items = ['Option Buying Power', '$2,206.94']

        result = self.open_acc.get_summary_data(items)
        print 'items: %s, result: %s' % (items, result)

        self.assertEqual(result, items[1])

    def test_set_summary(self):
        """
        Test set summary into class
        """
        self.open_acc.set_summary()
        summary = self.open_acc.summary

        print 'account summary:'
        pprint(summary)

        self.assertEqual(len(summary), 5)

        for key, item in summary.items():
            self.assertIn(key, self.open_acc.summary_keys)
            self.assertEqual(type(item), float)

    def test_convert_date(self):
        """
        Test convert date format into YYYY-MM-DD
        """
        dates = ['7/29/14', '11/4/13', '9/8/12', '1/26/13', '7/30/14']

        for date in dates:
            result = self.open_acc.convert_date(date)

            print 'date: %s, result: %s' % (date, result)

    def test_convert_datetime(self):
        """
        Test convert date format into YYYY-MM-DD
        """
        dates = [
            '7/25/14 21:55:09', '11/4/13 02:54:13', '9/8/12 21:38:24',
            '1/26/13 21:37:06', '7/30/14 05:54:58'
        ]

        for date in dates:
            result = self.open_acc.convert_datetime(date)

            print 'date: %s, result: %s' % (date, result)

    def test_convert_specific_type(self):
        """
        Test convert specific type for dict in a list
        """
        items = [
            {'a': 0, 'ref_no': 793403165.0, 'c': 0},
            {'a': 0, 'ref_no': 801854049.0, 'c': 0},
            {'a': 0, 'ref_no': 802092476.0, 'c': 0},
            {'a': 0, 'ref_no': 17.0, 'c': 0},
            {'a': 0, 'ref_no': 123.0, 'c': 0},
        ]

        self.open_acc.cash_balance = [dict(i) for i in items]

        self.open_acc.convert_specific_type(self.open_acc.cash_balance, 'ref_no', int, 0)

        for item, result in zip(items, self.open_acc.cash_balance):
            print 'dict: %s, result: %s' % (item, result)

            self.assertEqual(item['ref_no'], result['ref_no'])
            self.assertNotEqual(type(item['ref_no']), type(result['ref_no']))

    def set_sections(self, method, prop, length, keys):
        """
        Test set section into class property
        """
        getattr(self.open_acc, method)()

        order_history = getattr(self.open_acc, prop)

        print 'property: %s' % prop
        print 'method: %s' % method
        print 'item length: %d' % length
        print 'prop length: %s' % len(order_history)
        print 'keys: %s\n' % keys

        self.assertEqual(type(order_history), list)
        self.assertGreaterEqual(len(order_history), 0)

        for o in order_history:
            print o

            self.assertEqual(len(o), length)
            self.assertEqual(type(o), dict)

            for key in o.keys():
                self.assertIn(key, keys)

    def test_set_trade_history(self):
        """
        Test set trade history
        """
        self.set_sections(
            method='set_trade_history',
            prop='trade_history',
            length=12,
            keys=self.open_acc.trade_history_keys
        )

    def test_set_profits_losses(self):
        """
        Test set profits and losses into class property
        """
        self.set_sections(
            method='set_profits_losses',
            prop='profits_losses',
            length=8,
            keys=self.open_acc.profits_losses_keys
        )

    def test_set_options(self):
        """
        Test set profits and losses into class property
        """
        self.set_sections(
            method='set_options',
            prop='options',
            length=9,
            keys=self.open_acc.options_keys
        )

    def test_set_equities(self):
        """
        Test set profits and losses into class property
        """
        self.set_sections(
            method='set_equities',
            prop='equities',
            length=6,
            keys=self.open_acc.equity_keys
        )

    def test_set_order_history(self):
        """
        Test set order history
        """
        self.set_sections(
            method='set_order_history',
            prop='order_history',
            length=13,
            keys=self.open_acc.order_history_keys
        )

    def test_set_cash_balance(self):
        """
        Test set cash balance
        """
        self.set_sections(
            method='set_cash_balance',
            prop='cash_balance',
            length=9,
            keys=self.open_acc.cash_balance_keys
        )

    def test_set_futures(self):
        """
        Test set futures, currently testing paper money

        on real account
        Futures Statements
        Trade Date,Exec Date,Exec Time,Type,Ref #,Description,Fees,Commissions,Amount,Balance

        on paper money
        Futures
        Symbol,Description,SPC,Exp,Qty,Trade Price,Mark,P/L Day
        """
        self.set_sections(
            method='set_futures',
            prop='futures',
            length=10,  # for real money, use 10
            keys=self.open_acc.holding_future_keys  # for real money, use real_futures_keys
        )

    def test_set_forex(self):
        """
        Test set forex
        """
        self.set_sections(
            method='set_forex',
            prop='forex',
            length=9,
            keys=self.open_acc.forex_keys
        )

    def test_read(self):
        """
        Test most important part in class
        """
        keys = ['cash_balance', 'futures', 'forex', 'order_history',
                'trade_history', 'equities', 'options', 'summary', 'profits_losses']

        for fname in self.fnames:
            path = os.path.join(FILES['account_statement'], fname)

            print 'fname: %s' % fname
            print 'path: %s' % path

            data = open(path).read()

            open_acc = OpenAcc(data=data)

            result = open_acc.read()
            self.assertEqual(type(result), dict)
            self.assertEqual(len(result), 9)

            pprint(result, width=200)

            for key in result.keys():
                if key == 'summary':
                    self.assertEqual(type(result[key]), dict)
                else:
                    self.assertEqual(type(result[key]), list)

                self.assertIn(key, keys)

            print '\n' + '-' * 100 + '\n'

    def test_set_order_history_with_fix_file(self):
        """
        Test set order history
        """
        self.test_file = r'C:\Users\Jack\Projects\rivers\pms_app\tests\2014-10-31\2014-10-31-AccountStatement.csv'
        self.sample_data = open(self.test_file).read()
        self.open_acc = OpenAcc(data=self.sample_data)

        self.set_sections(
            method='set_order_history',
            prop='order_history',
            length=13,
            keys=self.open_acc.order_history_keys
        )
