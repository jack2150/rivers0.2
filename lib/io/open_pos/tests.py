import os
from django.test import TestCase
from rivers.settings import FILES
from lib.io.open_pos import OpenPos


# noinspection PyPep8Naming
class TestOpenPosCSV(TestCase):
    def setUp(self):
        print '=' * 100
        print "%s: currently run: %s" % (self.__class__.__name__, self._testMethodName)
        print '-' * 100 + '\n'

        test_file = os.path.join(FILES['position_statement'], '2014-08-01-PositionStatement.csv')
        self.open_csv = OpenPos(fname=test_file)

    def tearDown(self):
        print '\n' + '=' * 100 + '\n\n'

        del self.open_csv

    def test_read_lines_from_file(self):
        """
        Test read lines from file with test file
        """
        lines = self.open_csv.read_lines_from_file()

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

    def test_is_positions(self):
        """
        Test using list decide it is positions or not
        """
        items = [
            ['TSLA', '', '', '', '', '', '5.18', '-.12', '1.29',
             '-1.06', '+4.46%', '$8.00', '$8.00', '($250.00)'],
            ['TSLA', '', '', '', '', '', '5.18', '-.12', '1.29',
             '-1.06', '+4.46%', '$8.00', '$8.00'],
            ['Instrument', '', '', '', '', '', '5.18', '-.12', '1.29',
             '-1.06', '+4.46%', '', '', '($250.00)'],
        ]

        for key, item in enumerate(items):
            result = self.open_csv.is_positions(item)

            print 'items: %s' % item
            print 'result: %s\n' % result

            if key == 0:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

    def test_get_first_items(self):
        """
        Test get first item in a list
        """
        items = ['TSLA', '', '', '', '', '', '5.18', '-.12', '1.29']
        result = self.open_csv.get_first_items(items)

        print 'items: %s' % items
        print 'result: %s' % result

        self.assertEqual(result, 'TSLA')
        self.assertEqual(type(result), str)

    def test_is_instrument(self):
        """
        Test check the lines is instrument using first item
        """
        items = [
            'TSLA',
            'ISHARES MSCI EAFE ETF',
            '100 AUG 14 69 CALL'
        ]

        for key, item in enumerate(items):
            result = self.open_csv.is_instrument(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), bool)

            if key == 0:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

    def test_is_stock(self):
        """
        Test check the lines is stock using first item
        """
        items = [
            'TSLA',
            'ISHARES MSCI EAFE ETF',
            '100 AUG 14 69 CALL'
        ]

        for key, item in enumerate(items):
            result = self.open_csv.is_stock(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), bool)

            if key == 1:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

    def test_is_options(self):
        """
        Test check the lines is options using first item
        """
        items = [
            'TSLA',
            'ISHARES MSCI EAFE ETF',
            '100 AUG 14 69 CALL'
        ]

        for key, item in enumerate(items):
            result = self.open_csv.is_options(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), bool)

            if key == 2:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

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

    def test_options_is_normal_contract(self):
        """
        Test check options is normal contract or not
        """
        items = [
            ['100', 'AUG', '14', '67.5', 'CALL'],
            ['100', 'Weeklys', 'AUG1', '14', '50', 'PUT']
        ]

        for key, item in enumerate(items):
            result = self.open_csv.options_is_normal_contract(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), bool)

            if key == 0:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

    def test_add_normal_to_options_name(self):
        """
        Test add item into first position in list
        """
        items = [
            [1, 2, 3, 4],
            ['a', 'b', 'c'],
            ['100', 'AUG', '14', '67.5', 'CALL'],
        ]

        for item in items:
            print 'item before: %s' % item
            self.open_csv.add_normal_to_options_name(item)
            print 'item after: %s\n' % item

            self.assertEqual(item[1], 'Normal')

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

    def test_make_options_name_dict(self):
        """
        Test make options name from list into dict
        """
        items = [
            ['100', 'Normal', 'AUG', '14', '67.5', 'CALL'],
            ['100', 'Weeklys', 'AUG1', '14', '50', 'PUT']
        ]

        columns = [
            'right',
            'special',
            'ex_month',
            'ex_year',
            'strike_price',
            'contract'
        ]

        for item in items:
            result = self.open_csv.make_options_name_dict(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), dict)

            for column in columns:
                self.assertIn(column, result.keys())

    def test_format_option_contract(self):
        """
        Test format option contract that split name into 5 parts
        :return:
        """
        items = [
            '100 AUG 14 67.5 CALL',
            '100 (Weeklys) AUG1 14 50 PUT',
            '100 AUG 14 26.5 CALL'
        ]

        for item in items:
            result = self.open_csv.format_option_contract(item)

            print 'item: %s' % item
            print 'result: %s' % result
            print 'result length: %d' % len(result)
            print 'result type: %s\n' % type(result)

            self.assertEqual(len(result), 6)
            self.assertEqual(type(result), dict)

    def test_make_pos_dict(self):
        """
        Test make positions dict using list item
        """
        items = ['TSLA', '', '', '', '', '', '5.18', '-.12', '1.29',
                 '-1.06', '+4.46%', '$8.00', '$8.00', '($250.00)']
        result = self.open_csv.make_pos_dict(items)

        print 'item: %s' % items
        print 'result:'
        for k, r in result.items():
            print '%s: "%s"' % (k, r)
            self.assertIn(k, self.open_csv.position_columns)

        self.assertEqual(len(result), 14)
        self.assertEqual(type(result), dict)

    def test_reset_stock_and_options(self):
        """
        Test reset that return empty list and dict
        """
        stock, options = self.open_csv.reset_stock_and_options()

        print 'stock type: %s' % type(stock)
        print 'stock length: %s\n' % len(stock)

        self.assertEqual(type(stock), dict)
        self.assertFalse(len(stock))

        print 'options type: %s' % type(options)
        print 'options length: %s' % len(options)

        self.assertEqual(type(options), list)
        self.assertFalse(len(options))

    def test_reset_symbol_and_instrument(self):
        """
        Test reset that result str and dict
        """
        symbol, instrument = self.open_csv.reset_symbol_and_instrument()

        print 'symbol type: %s' % type(symbol)
        print 'symbol length: %s\n' % len(symbol)

        self.assertEqual(type(symbol), str)
        self.assertFalse(len(symbol))

        print 'instrument type: %s' % type(instrument)
        print 'instrument length: %s' % len(instrument)

        self.assertEqual(type(instrument), dict)
        self.assertFalse(len(instrument))

    def test_format_positions(self):
        """
        Test format position that ready for insert db
        """
        items = [
            ['ORACLE CORP COM', '0', '', '.00', '40.39', '-.57', '.00', '.00',
             '.00', '.00', '', '$0.00', '$0.00', ''],
            ['100 AUG 14 76 CALL', '+1', '15', '.54', '.36', '-.61', '22.01',
             '10.16', '-2.58', '4.57', '', '($18.00)', '($18.00)', ''],
            ['100 AUG 14 67.5 CALL', '+2', '15', '.37', '.31', 'N/A', '58.46',
             '39.94', '-3.41', '9.57', '', '($12.00)', '($12.00)', '']
        ]

        for item in items:
            result = self.open_csv.format_positions(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertNotIn('N/A', result)
            self.assertNotIn('', result)
            self.assertNotIn('$', result)
            self.assertNotIn('(', result)
            self.assertNotIn(')', result)

    def test_get_company_name(self):
        """
        Test get company name from list
        :return:
        """
        stock = {'mark_change': '-1.19', 'name': 'CELGENE CORP COM', 'pl_open': '$0.00',
                 'days': '', 'mark': '87.15', 'vega': '.00', 'pl_day': '$0.00',
                 'delta': '.00', 'bp_effect': '', 'theta': '.00', 'pct_change': '',
                 'quantity': '0', 'gamma': '.00', 'trade_price': '.00'}

        result = self.open_csv.get_company_name(stock)

        print 'stock: %s' % stock
        print 'result: %s' % result

        self.assertEqual(result, 'CELGENE CORP COM')
        self.assertEqual(type(result), str)

    def test_set_pos(self):
        """
        Test set positions into class with instrument, stock and options
        """
        symbol = 'CELG'

        instrument = {'mark_change': '', 'name': 'CELG', 'pl_open': '($7.50)',
                      'days': '', 'mark': '', 'vega': '-.25', 'pl_day': '($13.00)',
                      'delta': '12.41', 'bp_effect': '($150.00)', 'theta': '.00',
                      'pct_change': '-1.35%', 'quantity': '', 'gamma': '-.54',
                      'trade_price': ''}

        stock = {'mark_change': '-1.19', 'name': 'CELGENE CORP COM', 'pl_open': '$0.00',
                 'days': '', 'mark': '87.15', 'vega': '.00', 'pl_day': '$0.00',
                 'delta': '.00', 'bp_effect': '', 'theta': '.00', 'pct_change': '',
                 'quantity': '0', 'gamma': '.00', 'trade_price': '.00'}

        options = [{'mark_change': '+.46', 'name': '100 AUG 14 86 PUT', 'pl_open': '$13.50',
                    'days': '15', 'mark': '1.395', 'vega': '7.02', 'pl_day': '$46.00',
                    'delta': '-39.37', 'bp_effect': '', 'theta': '-5.72', 'pct_change': '',
                    'quantity': '+1', 'gamma': '7.94', 'trade_price': '1.26'},
                   {'mark_change': '+.59', 'name': '100 AUG 14 87.5 PUT', 'pl_open': '($21.00)',
                    'days': '15', 'mark': '2.05', 'vega': '-7.27', 'pl_day': '($59.00)',
                    'delta': '51.78', 'bp_effect': '', 'theta': '5.72', 'pct_change': '',
                    'quantity': '-1', 'gamma': '-8.49', 'trade_price': '1.84'}]

        self.open_csv.set_pos(symbol, instrument, stock, options)

        positions = self.open_csv.positions

        for pos in positions:
            self.assertEqual(pos['Symbol'], symbol)
            self.assertIn('Symbol', pos.keys())
            self.assertIn('Company', pos.keys())
            self.assertIn('Instrument', pos.keys())
            self.assertIn('Stock', pos.keys())
            self.assertIn('Options', pos.keys())

            print 'Symbol: %s' % pos['Symbol']
            print 'Company: %s' % pos['Company']
            print 'Instrument: %s' % pos['Instrument']
            print 'Stock: %s' % pos['Stock']
            print 'Options: %s' % pos['Options']

    def test_set_pos_from_lines(self):
        """
        Test open pos csv files then get instrument, stock, options
        and set it into class property
        """
        self.open_csv.set_pos_from_lines()

        positions = self.open_csv.positions

        self.assertEqual(len(positions), 21)

        for pos in positions:
            self.assertIn('Symbol', pos.keys())
            self.assertIn('Company', pos.keys())
            self.assertIn('Instrument', pos.keys())
            self.assertIn('Stock', pos.keys())
            self.assertIn('Options', pos.keys())

            print 'Symbol: %s' % pos['Symbol']
            print 'Company: %s' % pos['Company']
            print 'Instrument: %s' % pos['Instrument']
            print 'Stock: %s' % pos['Stock']
            print 'Options: %s' % pos['Options']
            print ''

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

    def test_is_overall(self):
        """
        Test the line is overall or not
        """
        items = [
            ['OVERNIGHT FUTURES BP', '$1873.49'],
            ['Position Statement for 865073982 () on 8/1/14 04:55:00'],
            ['BP ADJUSTMENT', '$0.00']
        ]

        for item in items:
            result = self.open_csv.is_overall(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            if len(item) == 2:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

    def test_get_overall_data_only(self):
        """
        Test return overall data only, do not return columns
        """
        items = [
            ['OVERNIGHT FUTURES BP', '$1873.49'],
            ['BP ADJUSTMENT', '$0.00']
        ]

        for item in items:
            result = self.open_csv.get_overall_data_only(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), str)
            self.assertEqual(result, item[1])

    def test_format_overall(self):
        """
        Test format overall that remove symbols_ui and signs
        """
        items = ['$3773.49', '($5609.52)', '$0.00', '$1873.49', '$1873.49']

        for item in items:
            result = self.open_csv.format_overall_item(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), float)

    def test_make_overall_dict(self):
        """
        Test using overall data list and make dict
        """
        items = [
            '$3773.49',
            '($5609.52)',
            '$0.00',
            '$1873.49',
            '$1873.49'
        ]

        result = self.open_csv.make_overall_dict(items)

        print 'items: %s\n' % items
        print 'result:'
        for k, r in result.items():
            print k, r

        print ''
        print 'result length: %d' % len(result)
        print 'result type: %s' % type(result)

        self.assertEqual(type(result), dict)
        self.assertEqual(len(result), 5)

        columns_name = [
            'cash_sweep',
            'pl_ytd',
            'bp_adjustment',
            'futures_bp',
            'available'
        ]

        for name in columns_name:
            self.assertIn(name, result.keys())

    def test_set_overall(self):
        """
        Test set overall into class property
        """
        items = ['$3773.49', '($5609.52)', '$0.00', '$1873.49', '$1873.49']
        self.open_csv.set_overall(items)

        overall = self.open_csv.overall

        print 'overall type: %s' % type(overall)
        print 'overall length: %d' % len(overall)

        self.assertEqual(type(overall), dict)
        self.assertEqual(len(overall), 5)

        print '\n' + 'overall dict:'
        for k, o in overall.items():
            print '%s: %s' % (k, o)

    def test_set_overall_from_lines(self):
        """
        Test open csv files and set overall property
        """
        self.open_csv.set_overall_from_lines()

        overall = self.open_csv.overall

        print 'overall type: %s' % type(overall)
        print 'overall length: %d' % len(overall)

        self.assertEqual(type(overall), dict)
        self.assertEqual(len(overall), 5)

        print '\n' + 'overall dict:'
        for k, o in overall.items():
            print '%s: %s' % (k, o)

    def test_read(self):
        """
        Final test, read csv files and return positions and overall dict
        """
        positions, overall = self.open_csv.read()

        print 'positions type: %s' % type(positions)
        print 'positions length: %d\n' % len(positions)

        for position in positions:
            for key, item in position.items():
                if key == 'Symbol' or key == 'Company':
                    self.assertEqual(type(item), str)
                elif key == 'Instrument' or key == 'Stock':
                    self.assertEqual(type(item), dict)
                    self.assertIn(len(item), (0, 14))
                elif key == 'Options':
                    self.assertEqual(type(item), list)

            self.assertIn('Symbol', position.keys())
            self.assertIn('Company', position.keys())
            self.assertIn('Instrument', position.keys())
            self.assertIn('Stock', position.keys())
            self.assertIn('Options', position.keys())

            print 'Symbol: %s' % position['Symbol']
            print 'Company: %s' % position['Company']
            print 'Instrument: %s' % position['Instrument']
            print 'Stock: %s' % position['Stock']
            print 'Options: %s' % position['Options']
            print ''

        # overall section
        print '\n' + 'overall type: %s' % type(overall)
        print 'overall length: %d' % len(overall)

        self.assertEqual(type(overall), dict)
        self.assertEqual(len(overall), 5)

        print '\n' + 'overall dict:'
        print overall

    def test_stock_only_files(self):
        """
        Test ready stock only files
        """
        test_date = '2014-03-10'
        test_path = os.path.join(FILES['position_statement'], 'tests', '2014-03-10-stock.csv')

        print 'file date: %s' % test_date
        print 'file path: %s\n' % test_path

        open_csv = OpenPos(fname=test_path)

        positions, overalls = open_csv.read()

        for position in positions:
            for key, item in position.items():
                if key == 'Symbol' or key == 'Company':
                    self.assertEqual(type(item), str)
                elif key == 'Instrument' or key == 'Stock':
                    self.assertEqual(type(item), dict)
                    self.assertIn(len(item), (0, 14))
                elif key == 'Options':
                    self.assertEqual(type(item), list)

            for key in ['Symbol', 'Company', 'Instrument', 'Stock', 'Options']:
                self.assertIn(key, position.keys())
                print '%s found in positions!' % key

            print ''

    def test_ready_multiple_files(self):
        """
        Test read on all files inside tos.pos
        """
        files = [
            '2014-03-07-closed.csv',
            '2014-03-10-stock.csv',
            '2014-03-11-hedge.csv',
            '2014-03-12-one-leg.csv',
            '2014-03-13-two-legs.csv',
            '2014-03-14-three-legs.csv',
            '2014-03-17-four-legs-part-1.csv'
        ]

        for f in files:
            open_csv = OpenPos(fname=os.path.join(FILES['position_statement'], 'tests', f))

            pos, ov = open_csv.read()

            print 'fname: %s' % f
            print 'positions length: %d' % len(pos)
            print 'overall length: %d\n' % len(ov)

            self.assertGreater(len(pos), 1)
            self.assertEqual(len(ov), 5)

    def test_2014_09_06_file(self):
        f = os.path.join(FILES['position_statement'], '2014-09-06-PositionStatement.csv')

        open_csv = OpenPos(fname=f)

        pos, ov = open_csv.read()

        print 'fname: %s' % f
        print 'positions length: %d' % len(pos)
        print 'overall length: %d\n' % len(ov)