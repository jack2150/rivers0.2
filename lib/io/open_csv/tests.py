import os
from pprint import pprint
from lib.test import TestSetUp
from rivers.settings import FILES
from lib.io.open_csv import OpenCSV


class TestOpenCSV(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.pos_file = os.path.join(
            FILES['position_statement'], '2014-08-01-PositionStatement.csv'
        )
        self.acc_file = os.path.join(
            FILES['account_statement'], '2014-07-23-AccountStatement.csv'
        )

        self.pos_data = open(self.pos_file, mode='r').read()
        self.acc_data = open(self.acc_file, mode='r').read()

        self.open_csv = OpenCSV(data=self.pos_data)

    def test_property(self):
        """
        Test property inside class
        """
        print 'data: %s' % self.open_csv.lines

        self.assertEqual(type(self.open_csv.lines), list)
        self.assertGreater(len(self.open_csv.lines), 0)

    def test_read_lines_from_file(self):
        """
        Test read lines from file with test file
        """
        self.open_csv.read_lines_from_file(fname=self.pos_file)
        lines = self.open_csv.lines

        print 'lines type: %s' % type(lines)
        print 'lines length: %d\n' % len(lines)
        print 'first 5 rows in lines:'

        for line in lines[:5]:
            print '\t"' + line + '"'

        self.assertTrue(len(lines))
        self.assertEqual(type(lines), list)

    def test_replace_dash_inside_quote(self):
        """
        Test replace dash inside quote
        example "$1,254.00" become $1254.00
        """
        line = 'OVERNIGHT FUTURES BP,"$1,653.36"'
        result = self.open_csv.replace_dash_inside_quote(line)

        print 'line: %s' % line
        print 'result: %s' % result

        self.assertNotIn('"', result)

    def test_split_lines_with_dash(self):
        """
        Test split line using dash into list of items
        """
        line = 'TSLA,,,,,,5.18,-.12,1.29,-1.06,+4.46%,$8.00,$8.00,($250.00)'
        result = self.open_csv.split_lines_with_dash(line)

        print 'line: %s' % line
        print 'result: %s' % result
        print 'type: %s' % type(result)
        print 'length: %d' % len(result)

        self.assertEqual(len(result), 14)
        self.assertEqual(type(result), list)

    def test_remove_bracket_then_add_negative(self):
        """
        Test remove brackets '()' on str item then add negative
        """
        item = '($5609.52)'
        result = self.open_csv.remove_bracket_then_add_negative(item)

        print 'item: %s' % item
        print 'result: %s' % result

        self.assertNotIn('(', result)
        self.assertNotIn(')', result)
        self.assertIn('-', result)

    def test_remove_dollar_symbols(self):
        """
        Test remove dollar symbol on str item
        """
        item = '3773.49'
        result = self.open_csv.remove_dollar_symbols(item)

        print 'item: %s' % item
        print 'result: %s' % result

        self.assertNotIn('$', result)

    def test_remove_percent_symbols(self):
        """
        Test remove dollar symbol on str item
        """
        item = '+1.77%'
        result = self.open_csv.remove_percent_symbols(item)

        print 'item: %s' % item
        print 'result: %s' % result

        self.assertNotIn('%', result)

    def test_split_str_with_space(self):
        """
        Test split str with space
        """
        items = [
            '100 AUG 14 67.5 CALL',
            '100 (Weeklys) AUG1 14 50 PUT',
            '100 AUG 14 26.5 CALL'
        ]

        for item in items:
            result = self.open_csv.split_str_with_space(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), list)
            self.assertIn(len(result), (5, 6))

    def test_remove_brackets_only(self):
        """
        Test remove brackets on options name
        """
        items = [
            '100 AUG 14 47 PUT',
            '100 (Weeklys) AUG2 14 1990 CALL',
            '100 (Mini) AUG1 14 20 PUT',
        ]

        for item in items:
            result = self.open_csv.remove_brackets_only(item)

            print 'item: %s' % item
            print 'result: %s' % result

            self.assertNotIn('(', result)
            self.assertNotIn(')', result)

    def test_last_five_lines(self):
        """
        Test using a list of lines get last 5 items
        """
        lines = range(10)
        result = self.open_csv.last_five_lines(lines)

        print 'lines type: %s' % type(result)
        print 'lines length: %s' % len(result)

        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 5)

        pprint(result)
        pprint(self.open_csv.last_five_lines(self.open_csv.lines))

    def test_convert_float_or_str(self):
        """
        Test convert item into float or string
        """
        items = ['12.24', 'VXX', '02:49:35', '956.98', 'JUL4 14']

        for item in items:
            result = self.open_csv.convert_float_or_str(item)

            print 'item: %s, result: %s, type: %s' % (
                item, result, type(result)
            )

            self.assertIn(type(result), [str, float])

    def test_format_item(self):
        """
        Test format item that remove all unnecessary symbol
        """
        items = ['($56.50)', '-17.86%', '$0.00', '+1', 'AUG 14']

        for item in items:
            result = self.open_csv.format_item(item)

            print 'item: %s, result: %s, type: %s' % (
                item, result, type(result)
            )

            self.assertIn(type(result), [str, float])

            result = str(result)
            self.assertNotIn('%', result)
            self.assertNotIn('$', result)
            self.assertNotIn('(', result)
            self.assertNotIn(')', result)

    def test_get_lines(self):
        """
        Test get lines section from lines
        """
        self.open_csv = OpenCSV(self.acc_data)

        phrases = [
            ('Profits and Losses', 'OVERALL TOTALS'),
            ('Options', ',,,,,,'),
            ('Equities', 'OVERALL TOTALS'),
            ('Account Trade History', None),
            ('Account Order History', None),
            ('Forex Statements', None),
            ('Futures Statements', None),
            ('Cash Balance', 'TOTAL')
        ]

        for start, end in phrases:
            lines = self.open_csv.get_lines(start, end)
            print start, end

            for line in lines:
                print line

            print '-' * 100

    def test_make_dict(self):
        """
        Test make dict using keys and values
        """
        keys = ['symbol', 'description', 'pl_open', 'pl_pct', 'pl_day', 'pl_ytd', 'margin_req']
        values = ['AA', 'ALCOA INC COM', 0.0, 0.0, 0.0, -271.98, 0.0]

        print 'keys: %s' % keys
        print 'values: %s' % values

        result = self.open_csv.make_dict(keys, values)
        print 'result: %s' % result

        for key, value in result.items():
            self.assertIn(key, keys)
            self.assertIn(value, values)

            index = keys.index(key)

            self.assertEqual(key, keys[index])
            self.assertEqual(value, values[index])

    def test_del_empty_keys(self):
        """
        Test delete empty key in dict
        """
        items = {'': '', 'ggg': 'hhh', 'kkk': 'lll'}

        result = self.open_csv.del_empty_keys(items)

        print 'items: %s' % items
        print 'result: %s' % result

        self.assertGreater(len(items), len(result))
        self.assertNotIn('', result.keys())

    def test_fillna_dict(self):
        """
        Test fill empty or none value in dict
        """
        self.open_csv = OpenCSV(self.acc_data)
        self.open_csv.trade_history = list()

        trade_history_keys = [
            '', 'execute_time', 'spread', 'side', 'quantity',
            'pos_effect', 'symbol', 'expire_date', 'strike',
            'contract', 'price', 'net_price', 'order_type'
        ]

        self.open_csv.set_values(
            start_phrase='Account Trade History',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=trade_history_keys,
            prop_name='trade_history'
        )

        before_fillna = self.open_csv.trade_history
        after_fillna = self.open_csv.fillna_dict(self.open_csv.trade_history)
        after_fillna = map(self.open_csv.del_empty_keys, after_fillna)

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

    def test_set_values(self):
        """
        Test open files, get lines section, format data,
        make dict and finally set values in property
        """
        self.open_csv = OpenCSV(self.acc_data)
        self.open_csv.trade_history = list()

        trade_history_keys = [
            '', 'execute_time', 'spread', 'side', 'quantity',
            'pos_effect', 'symbol', 'expire_date', 'strike',
            'contract', 'price', 'net_price', 'order_type'
        ]

        start_phrase = 'Account Trade History'
        end_phrase = None
        start_add = 2
        end_reduce = -1
        prop_name = 'trade_history'

        print 'start phrase: %s, end phrase: %s' % (start_phrase, end_phrase)
        print 'start add: %d, end reduce: %d' % (start_add, end_reduce)
        print 'property name: %s' % prop_name

        self.open_csv.set_values(
            start_phrase=start_phrase,
            end_phrase=end_phrase,
            start_with=start_add,
            end_until=end_reduce,
            prop_keys=trade_history_keys,
            prop_name=prop_name
        )

        trade_history = self.open_csv.trade_history

        lines = self.open_csv.get_lines('Account Trade History')

        print ''
        for tk in trade_history:
            print tk
            self.assertEqual(type(tk), dict)
            self.assertEqual(len(tk), 13)

        self.assertEqual(len(lines), len(trade_history) + 2 + 1)
        self.assertEqual(type(trade_history), list)
