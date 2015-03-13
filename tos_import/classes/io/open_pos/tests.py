import os
from glob import glob
from pprint import pprint

from tos_import.files.test_files import test_pos_path, test_path
from tos_import.classes.tests import TestSetUp
from tos_import.classes.io.open_pos import OpenPos



# noinspection PyUnresolvedReferences
class TestOpenPos(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.fnames = glob(os.path.join(test_pos_path + '/*.csv'))
        self.pos_data = open(self.fnames[0]).read()
        self.open_pos = OpenPos(data=self.pos_data)

    def test_all(self):
        for key, fname in enumerate(self.fnames):
            print '%d. fname: %s' % (key, fname)
            print ''

            self.pos_data = open(fname).read()
            self.open_pos = OpenPos(data=self.pos_data)

            self.test_set_future_position()
            self.test_set_forex_position()
            self.test_set_position_summary()
            self.test_set_equity_option_position()

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
            result = self.open_pos.is_instrument(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), bool)

            if key == 0:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

    def test_is_equity(self):
        """
        Test check the lines is stock using first item
        """
        items = [
            'TSLA',
            'ISHARES MSCI EAFE ETF',
            '100 AUG 14 69 CALL'
        ]

        for key, item in enumerate(items):
            result = self.open_pos.is_equity(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), bool)

            if key == 1:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

    def test_is_option(self):
        """
        Test check the lines is options using first item
        """
        items = [
            'TSLA',
            'ISHARES MSCI EAFE ETF',
            '100 AUG 14 69 CALL'
        ]

        for key, item in enumerate(items):
            result = self.open_pos.is_option(item)

            print 'item: %s' % item
            print 'result: %s\n' % result

            self.assertEqual(type(result), bool)

            if key == 2:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

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
            result = self.open_pos.format_option_contract(item)

            print 'item: %s' % item
            print 'result: %s' % result
            print 'result length: %d' % len(result)
            print 'result type: %s\n' % type(result)

            self.assertEqual(len(result), 6)
            self.assertEqual(type(result), dict)

            self.assertEqual(type(result['right']), int)
            self.assertEqual(type(result['ex_year']), int)
            self.assertEqual(type(result['strike']), float)

    def test_reset_position_set(self):
        """
        Test reset position set into blank dict
        """
        position_set = self.open_pos.reset_position_set()

        pprint(position_set)

        self.assertEqual(position_set['symbol'], '')
        self.assertEqual(position_set['company'], '')
        self.assertEqual(position_set['instrument'], None)
        self.assertEqual(position_set['equity'], None)
        self.assertEqual(position_set['options'], list())

    def test_append_equity_option_position(self):
        """
        Test append position set into equity option position
        """
        position_set = self.open_pos.reset_position_set()
        position_set['instrument'] = {
            'mark_change': 0.0, 'name': 'CELG', 'pl_open': -7.5, 'days': 0.0, 'mark': 0.0,
            'vega': -0.25, 'pl_day': -13.0, 'delta': 12.41, 'bp_effect': -150.0, 'theta': 0.0,
            'pct_change': -1.35, 'quantity': 0.0, 'gamma': -0.54, 'trade_price': 0.0
        }
        position_set['equity'] = {
            'mark_change': -1.19, 'name': 'CELGENE CORP COM', 'pl_open': 0.0, 'days': 0.0,
            'mark': 87.15, 'vega': 0.0, 'pl_day': 0.0, 'delta': 0.0, 'bp_effect': 0.0,
            'theta': 0.0, 'pct_change': 0.0, 'quantity': 0.0, 'gamma': 0.0, 'trade_price': 0.0
        }

        self.open_pos.append_equity_option_position(position_set)

        self.assertEqual(len(self.open_pos.equity_option_position), 1)

        print 'symbol: %s' % self.open_pos.equity_option_position[0]['symbol']
        print 'company: %s' % self.open_pos.equity_option_position[0]['company']

        self.assertEqual(
            self.open_pos.equity_option_position[0]['symbol'],
            position_set['instrument']['name']
        )

        self.assertEqual(
            self.open_pos.equity_option_position[0]['company'],
            position_set['equity']['name']
        )

        pprint(self.open_pos.equity_option_position, width=400)

    def set_sections(self, method, prop, lengths, keys):
        """
        Test set section into class property
        """
        getattr(self.open_pos, method)()

        test_prop = getattr(self.open_pos, prop)

        print 'property: %s' % prop
        print 'method: %s' % method
        print 'item length: ', lengths
        print 'prop length: %s' % len(test_prop)
        print 'keys: %s\n' % keys

        self.assertEqual(type(test_prop), list)
        self.assertGreaterEqual(len(test_prop), 0)

        for o in test_prop:
            print o

            self.assertIn(len(o), lengths)
            self.assertEqual(type(o), dict)

            for key in o.keys():
                self.assertIn(key, keys)

    def test_set_future_position(self):
        """
        Test set future position into class property
        """
        self.set_sections(
            method='set_future_position',
            prop='future_position',
            lengths=(15, ),
            keys=self.open_pos.future_position_keys + [
                'lookup', 'description', 'session'
            ]
        )

    def test_set_forex_position(self):
        """
        Test set forex position into class property
        """
        self.set_sections(
            method='set_forex_position',
            prop='forex_position',
            lengths=(10, ),  # with or without mark value
            keys=self.open_pos.forex_position_keys + ['description']
        )

    def test_set_position_summary(self):
        """
        Test set position summary into class property
        """
        self.open_pos.set_position_summary()

        self.assertEqual(type(self.open_pos.position_summary), dict)
        self.assertEqual(len(self.open_pos.position_summary), 5)
        for key in self.open_pos.position_summary_keys:
            self.assertIn(key, self.open_pos.position_summary.keys())

        print 'item length: ', len(self.open_pos.position_summary)
        print 'keys: %s\n' % self.open_pos.position_summary.keys()

        print 'position summary:'
        pprint(self.open_pos.position_summary)

    def test_set_equity_option_position(self):
        """
        Test set instrument, stock, option into class property
        """
        self.open_pos.set_equity_option_position()

        print 'position length: %d' % len(self.open_pos.equity_option_position)
        print 'position type: %s' % type(self.open_pos.equity_option_position)

        self.assertEqual(type(self.open_pos.equity_option_position), list)

        for position in self.open_pos.equity_option_position:
            print 'symbol: %s' % position['symbol']
            print 'company: %s' % position['company']
            print 'instrument:\n%s' % position['instrument']
            print 'equity:\n%s' % position['equity']
            print 'options:'
            pprint(position['options'], width=400)
            print ''

            self.assertNotEqual(position['symbol'], '')
            self.assertGreater(len(position['symbol']), 0)
            self.assertEqual(type(position['symbol']), str)
            self.assertNotEqual(position['company'], '')
            self.assertGreater(len(position['company']), 0)
            self.assertEqual(type(position['company']), str)

            self.assertEqual(len(position['instrument'].keys()), 14)
            self.assertEqual(type(position['instrument']), dict)

            if len(position['equity']):
                self.assertEqual(len(position['equity'].keys()), 14)
                self.assertEqual(type(position['equity']), dict)

            if len(position['options']):
                self.assertEqual(len(position['options'][0].keys()), 14)
                self.assertEqual(type(position['options']), list)
                self.assertEqual(type(position['options'][0]), dict)

            for key, value in position['instrument'].items():
                self.assertIn(key, self.open_pos.equity_option_keys)
                self.assertNotEqual(value, '')

            for key, value in position['equity'].items():
                self.assertIn(key, self.open_pos.equity_option_keys)
                self.assertNotEqual(value, '')

            for option in position['options']:
                for key, value in option.items():
                    self.assertIn(key, self.open_pos.equity_option_keys)
                    self.assertNotEqual(value, '')

    def test_read(self):
        """
        Test read position statement file and output dict data
        """
        self.fnames = self.fnames + [
            os.path.join(test_path, '2014-11-14/2014-11-14-PositionStatement.csv'),
            os.path.join(test_path, '2014-11-15/2014-11-15-PositionStatement.csv'),
        ]

        expected_keys = [
            'equity_option_position', 'future_position',
            'forex_position', 'position_summary'
        ]

        for file_no, fname in enumerate(self.fnames):
            print '%d. fname: %s\n' % (file_no, fname)

            pos_data = open(fname).read()
            open_pos = OpenPos(data=pos_data)

            pos = open_pos.read()

            for key in pos.keys():
                self.assertIn(key, expected_keys)

            print 'Equity and Option Position:'
            pprint(pos['equity_option_position'], width=400)

            print '\n' + 'Future Position:'
            pprint(pos['future_position'], width=400)

            print '\n' + 'Position Summary:'
            pprint(pos['position_summary'], width=400)

            print '\n' + 'Forex Position:'
            pprint(pos['forex_position'], width=400)

            print '-' * 100 + '\n'
