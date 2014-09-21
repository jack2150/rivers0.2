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

        self.test_file = os.path.join(FILES['account_statement'], self.fnames[0])

        self.open_acc = OpenAcc(fname=self.test_file)

    def test_property(self):
        """
        Test property inside class
        """
        properties = ['summary_keys', 'profits_losses_keys', 'options_keys',
                      'trade_history_keys', 'order_history_keys',
                      'forex_keys', 'futures_keys', 'cash_balance_keys']

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

    def test_set_values(self):
        """
        Test open files, get lines section, format data,
        make dict and finally set values in property
        """
        start_phrase = 'Account Trade History'
        end_phrase = None
        start_add = 2
        end_reduce = -1
        prop_name = 'trade_history'

        print 'start phrase: %s, end phrase: %s' % (start_phrase, end_phrase)
        print 'start add: %d, end reduce: %d' % (start_add, end_reduce)
        print 'property name: %s' % prop_name

        self.open_acc.set_values(
            start_phrase=start_phrase,
            end_phrase=end_phrase,
            start_add=start_add,
            end_reduce=end_reduce,
            prop_keys=self.open_acc.trade_history_keys,
            prop_name=prop_name
        )

        trade_history = self.open_acc.trade_history

        lines = self.open_acc.get_lines('Account Trade History')

        self.assertEqual(len(lines), len(trade_history) + 2 + 1)
        self.assertEqual(type(trade_history), list)

        print ''
        for tk in trade_history:
            print tk
            self.assertEqual(type(tk), dict)
            self.assertEqual(len(tk), 13)

    def test_fillna_history_sections(self):
        """
        Test fill empty or none value in dict
        """
        self.open_acc.set_values(
            start_phrase='Account Trade History',
            end_phrase=None,
            start_add=2,
            end_reduce=-1,
            prop_keys=self.open_acc.trade_history_keys,
            prop_name='trade_history'
        )

        before_fillna = self.open_acc.trade_history
        after_fillna = self.open_acc.fillna_history_sections(self.open_acc.trade_history)
        after_fillna = map(self.open_acc.del_empty_keys, after_fillna)

        for tk1, tk2 in zip(before_fillna, after_fillna):
            print tk1
            print tk2
            print ''

            self.assertIn('', tk1.values())
            self.assertNotIn('', tk2.values())

            for value1, value2 in zip(tk1.values(), tk2.values()):
                if value1 and (value1 != 'DEBIT' and value1 != 'CREDIT'):
                    self.assertIn(value1, tk2.values())

            for key in tk1.keys():
                if key:
                    self.assertIn(key, tk2.keys())

    def set_sections(self, method, prop, length, keys):
        """
        Test set section into class property
        """
        getattr(self.open_acc, method)()

        order_history = getattr(self.open_acc, prop)

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
            length=7,
            keys=self.open_acc.profits_losses_keys
        )

    def test_set_options(self):
        """
        Test set profits and losses into class property
        """
        self.set_sections(
            method='set_options',
            prop='options',
            length=7,
            keys=self.open_acc.options_keys
        )

    def test_set_equities(self):
        """
        Test set profits and losses into class property
        """
        self.set_sections(
            method='set_equities',
            prop='equities',
            length=4,
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
        Test set futures
        """
        self.set_sections(
            method='set_futures',
            prop='futures',
            length=10,
            keys=self.open_acc.futures_keys
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
                'trade_history', 'equities', 'options', 'summary']

        for fname in self.fnames:
            path = os.path.join(FILES['account_statement'], fname)

            print 'fname: %s' % fname
            print 'path: %s' % path

            open_acc = OpenAcc(path)

            result = open_acc.read()
            self.assertEqual(type(result), dict)
            self.assertEqual(len(result), 8)

            pprint(result, width=200)

            for key in result.keys():
                if key == 'summary':
                    self.assertEqual(type(result[key]), dict)
                else:
                    self.assertEqual(type(result[key]), list)

                self.assertIn(key, keys)

            print '\n' + '-' * 100 + '\n'