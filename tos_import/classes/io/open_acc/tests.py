from glob import glob
import os
from pprint import pprint
from tos_import.test_files import *
from tos_import.classes.test import TestSetUp
from tos_import.classes.io.open_acc import OpenAcc


class TestOpenAcc(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.fnames = glob(test_acc_path + '/*.csv') + [
            os.path.join(test_path, '2014-11-01', '2014-11-01-AccountStatement.csv'),
            os.path.join(test_path, '2014-11-19', '2014-11-19-AccountStatement.csv')
        ]

        self.test_file = self.fnames[0]
        self.sample_data = open(self.test_file).read()

        self.open_acc = OpenAcc(data=self.sample_data)

    def test_property(self):
        """
        Test property inside class
        """
        properties = ['account_summary_keys', 'forex_summary_keys',
                      'profit_loss_keys', 'holding_equity_keys',
                      'holding_option_keys', 'trade_history_keys',
                      'order_history_keys', 'future_statement_keys',
                      'holding_future_keys', 'forex_statement_keys',
                      'holding_forex_keys', 'cash_balance_keys']

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

    def test_set_account_summary(self):
        """
        Test set summary into class
        """
        self.open_acc.set_account_summary()
        summary = self.open_acc.account_summary

        print 'account summary:'
        pprint(summary)

        self.assertEqual(len(summary), 5)

        for key, item in summary.items():
            self.assertIn(key, self.open_acc.account_summary_keys)
            self.assertEqual(type(item), float)

    def test_set_forex_summary(self):
        """
        """
        self.open_acc.set_forex_summary()
        forex_summary = self.open_acc.forex_summary

        pprint(forex_summary)


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

    def set_sections(self, method, prop, lengths, keys):
        """
        Test set section into class property
        """
        getattr(self.open_acc, method)()

        order_history = getattr(self.open_acc, prop)

        print 'property: %s' % prop
        print 'method: %s' % method
        print 'item length: ', lengths
        print 'prop length: %s' % len(order_history)
        print 'keys: %s\n' % keys

        self.assertEqual(type(order_history), list)
        self.assertGreaterEqual(len(order_history), 0)

        for o in order_history:
            print o

            self.assertIn(len(o), lengths)
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
            lengths=(12, ),
            keys=self.open_acc.trade_history_keys
        )

    def test_get_future_detail(self):
        """
        Test get description, expire date and session from line
        """
        lines = [
            '/ESZ4,"E-mini S&P 500 Index Futures,Dec-2014,ETH",'
            '($212.50),-0.21%,($62.50),($450.00),"$5,060.00",($62.50)',
            '/YGZ4,Mini Gold Futures - ICUS - Dec14,$0.00,'
            '0.00%,$0.00,$0.00,"$1,650.00",$0.00'
        ]

        expected_results = [
            dict(
                lookup='ES',
                description='E-MINI S&P 500 INDEX FUTURES',
                expire_date='DEC-2014',
                session='ETH'
            ),
            dict(
                lookup='YG',
                description='MINI GOLD FUTURES',
                expire_date='DEC14',
                session='ICUS',
            )
        ]

        for line, expected_result in zip(lines, expected_results):
            result = self.open_acc.get_future_detail(line)

            print 'result:'
            print 'lookup: %s' % result['lookup']
            print 'description: %s' % result['description']
            print 'expire date: %s' % result['expire_date']
            print 'session: %s\n' % result['session']

            self.assertEqual(result['lookup'], expected_result['lookup'])
            self.assertEqual(result['description'], expected_result['description'])
            self.assertEqual(result['expire_date'], expected_result['expire_date'])
            self.assertEqual(result['session'], expected_result['session'])

    def test_set_profit_loss(self):
        """
        Test set profits and losses into class property
        """
        self.set_sections(
            method='set_profit_loss',
            prop='profit_loss',
            lengths=(7, 8),  # with or without mark value
            keys=self.open_acc.profit_loss_keys + [
                'expire_date', 'session'
            ]
        )

        pprint(self.open_acc.profit_loss, width=400)

    def test_set_holding_option(self):
        """
        Test set profits and losses into class property
        """
        self.set_sections(
            method='set_holding_option',
            prop='holding_option',
            lengths=(7, ),
            keys=self.open_acc.holding_option_keys
        )

    def test_set_holding_equity(self):
        """
        Test set profits and losses into class property
        """
        self.set_sections(
            method='set_holding_equity',
            prop='holding_equity',
            lengths=(4, 6),  # with or without mark and mark value
            keys=self.open_acc.holding_equity_keys
        )

    def test_set_order_history(self):
        """
        Test set order history
        """
        self.set_sections(
            method='set_order_history',
            prop='order_history',
            lengths=(13, ),
            keys=self.open_acc.order_history_keys
        )

    def test_set_cash_balance(self):
        """
        Test set cash balance
        """
        self.set_sections(
            method='set_cash_balance',
            prop='cash_balance',
            lengths=(9, ),
            keys=self.open_acc.cash_balance_keys
        )

    def test_set_future_statement(self):
        """
        Test set future statement not holding future
        """
        self.set_sections(
            method='set_future_statement',
            prop='future_statement',
            lengths=(10, ),  # for real money, use 10
            keys=self.open_acc.future_statement_keys  # for real money, use real_futures_keys
        )

    def test_get_lines_without_phrase(self):
        """
        Test get lines with using start text and end text
        """
        lines = self.open_acc.get_lines_without_phrase(
            start_with=('Futures', ),
            start_without=('Statements', '/'),
            end_phrase='OVERALL TOTALS',
        )

        self.assertIn('Futures', lines[0])
        for start_without in ('Statements', '/'):
            self.assertNotIn(start_without, lines[0])
        self.assertIn('OVERALL TOTALS', lines[-1])

        print 'Get lines result for holding future:'
        pprint(lines)
        print ''

        lines = self.open_acc.get_lines_without_phrase(
            start_with=('Forex', ),
            start_without=('Statements', '/'),
            end_phrase='OVERALL TOTALS',
        )
        self.assertIn('Forex', lines[0])
        for start_without in ('Statements', '/'):
            self.assertNotIn(start_without, lines[0])
        self.assertIn('OVERALL TOTALS', lines[-1])

        print 'Get lines result for holding forex:'
        pprint(lines)

    def test_set_holding_future(self):
        """
        Test set futures, currently testing paper money
        """
        self.set_sections(
            method='set_holding_future',
            prop='holding_future',
            lengths=(10, ),  # for real money, use 10
            keys=self.open_acc.holding_future_keys + ['session']
        )

    def test_set_forex_statement(self):
        """
        Test set forex statement
        """
        self.set_sections(
            method='set_forex_statement',
            prop='forex_statement',
            lengths=(9, ),
            keys=self.open_acc.forex_statement_keys
        )

    def test_set_holding_forex(self):
        """
        Test set forex
        """
        self.set_sections(
            method='set_holding_forex',
            prop='holding_forex',
            lengths=(6, ),
            keys=self.open_acc.holding_forex_keys
        )

    def test_read(self):
        """
        Test most important part in class
        """
        keys = [
            'account_summary', 'forex_summary', 'profit_loss', 'holding_option',
            'holding_equity', 'trade_history', 'order_history', 'cash_balance',
            'future_statement', 'holding_future', 'forex_statement', 'holding_forex',
        ]

        for fname in self.fnames[-1:]:
            print 'fname: %s' % fname

            data = open(fname).read()

            open_acc = OpenAcc(data=data)

            result = open_acc.read()
            self.assertEqual(type(result), dict)
            self.assertEqual(len(result), 12)

            pprint(result['holding_future'], width=400)


            #pprint(result, width=600)

            for key in result.keys():
                if key == 'account_summary' or key == 'forex_summary':
                    self.assertEqual(type(result[key]), dict)
                else:
                    self.assertEqual(type(result[key]), list)

                self.assertIn(key, keys)

            print '\n' + '-' * 100 + '\n'

    def test_set_order_history_with_fix_file(self):
        """
        Test set order history
        """
        self.test_file = test_path + r'/2014-10-31/2014-10-31-AccountStatement.csv'
        self.sample_data = open(self.test_file).read()
        self.open_acc = OpenAcc(data=self.sample_data)

        self.set_sections(
            method='set_order_history',
            prop='order_history',
            lengths=(13, ),
            keys=self.open_acc.order_history_keys
        )
