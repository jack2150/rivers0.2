from datetime import datetime
from glob import glob
import os
from pprint import pprint
from tos_import.test_files import *
from tos_import.classes.test import TestSetUp
from tos_import.classes.io.open_ta import OpenTA


class TestOpenTA(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.fnames = glob(os.path.join(test_ta_path, '/*.csv')) + [
            os.path.join(test_path, '2014-10-31', '2014-10-31-TradeActivity.csv'),
            os.path.join(test_path, '2014-11-01', '2014-11-01-TradeActivity.csv')
        ]

        self.test_file = self.fnames[0]
        self.test_data = open(self.test_file).read()

        self.open_ta = OpenTA(data=self.test_data)

    def set_sections(self, method, prop, length, keys):
        """
        Test set section into class property
        """
        getattr(self.open_ta, method)()

        order_history = getattr(self.open_ta, prop)

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

    def test_convert_hour_minute(self):
        """
        Test convert hour minute from string
        """
        samples = ['08:45', '09:00', '11:00', '14:45', '10:35']
        expects = ['08:45:00', '09:00:00', '11:00:00', '14:45:00', '10:35:00']

        for sample, expect in zip(samples, expects):
            print 'sample: %s' % sample
            print 'expect: %s' % expect

            result = self.open_ta.convert_hour_minute(sample)

            print 'result: %s\n' % result

            self.assertEqual(result, expect)

    def test_remove_working_order_rows(self):
        """
        Test remove empty quantity row in working order
        """
        self.open_ta.set_values(
            start_phrase='Working Orders',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.open_ta.working_order_keys,
            prop_name='working_order'
        )

        before_rows = len(self.open_ta.working_order)
        print 'before, working order row: %d' % before_rows
        self.assertGreaterEqual(before_rows, 0)

        print 'run remove empty quantity working order...\n'
        self.open_ta.remove_working_order_rows()

        for key, working_order in enumerate(self.open_ta.working_order):
            print 'row: %d, working order: %d' % (key, working_order['quantity'])
            self.assertTrue(working_order['quantity'])

        after_rows = len(self.open_ta.working_order)
        print '\n' + 'after, working order row: %d' % after_rows
        self.assertGreaterEqual(after_rows, before_rows)

    def test_set_working_order(self):
        """
        Test set working_order
        """
        self.set_sections(
            method='set_working_order',
            prop='working_order',
            length=14,
            keys=self.open_ta.working_order_keys
        )

        # correct data type
        for working_order in self.open_ta.working_order:
            self.assertEqual(type(working_order['quantity']), int)
            self.assertEqual(type(working_order['strike']), float)
            self.assertEqual(type(working_order['price']), float)

            self.assertIn(type(working_order['time_placed']), (datetime, type(None)))

    def test_set_filled_orders(self):
        """
        Test set filled_orders
        """
        self.set_sections(
            method='set_filled_order',
            prop='filled_order',
            length=12,
            keys=self.open_ta.filled_order_keys
        )

        # correct data type
        for filled_order in self.open_ta.filled_order:
            self.assertEqual(type(filled_order['quantity']), int)
            self.assertEqual(type(filled_order['strike']), float)
            self.assertEqual(type(filled_order['price']), float)
            self.assertEqual(type(filled_order['net_price']), float)
            self.assertEqual(type(filled_order['expire_date']), str)

            self.assertIn(type(filled_order['exec_time']), (datetime, type(None)))

    def test_set_cancelled_orders(self):
        """
        Test set cancelled_orders
        """
        self.set_sections(
            method='set_cancelled_order',
            prop='cancelled_order',
            length=13,
            keys=self.open_ta.cancelled_order_keys
        )

        # correct data type
        for cancelled_order in self.open_ta.cancelled_order:
            self.assertEqual(type(cancelled_order['quantity']), int)
            self.assertEqual(type(cancelled_order['strike']), float)
            self.assertEqual(type(cancelled_order['price']), float)
            self.assertEqual(type(cancelled_order['expire_date']), str)

            self.assertIn(type(cancelled_order['time_cancelled']), (datetime, type(None)))

    def sub_format_rolling_strategy(self, cls_name, keys_length, keys_list, not_in_key):
        """
        Test format rolling strategy options
        """
        self.open_ta.set_values(
            start_phrase='Rolling Strategies',
            end_phrase=None,
            start_with=2,
            end_until=None,
            prop_keys=self.open_ta.rolling_strategy_keys,
            prop_name='rolling_strategy'
        )

        before_keys_length = len(self.open_ta.rolling_strategy[0].keys())
        print 'rolling strategy length: %d' % len(self.open_ta.rolling_strategy)
        print 'rolling strategy columns: %d' % before_keys_length
        print 'rolling strategy: '
        pprint(self.open_ta.rolling_strategy, width=300)

        test_cls = getattr(self.open_ta, cls_name)
        test_cls()

        after_keys_length = len(self.open_ta.rolling_strategy[0].keys())
        print '\n' + 'rolling strategy length: %d' % len(self.open_ta.rolling_strategy)
        print 'rolling strategy columns: %d' % after_keys_length
        print 'rolling strategy: '
        pprint(self.open_ta.rolling_strategy, width=400)

        self.assertNotEqual(before_keys_length, after_keys_length)
        self.assertEqual(after_keys_length, keys_length)

        for x in keys_list:
            self.assertIn(x, self.open_ta.rolling_strategy[0].keys())

        self.assertNotIn(not_in_key, self.open_ta.rolling_strategy[0].keys())

    def test_format_rolling_strategy_options(self):
        """
        Test format rolling strategy options
        """
        self.sub_format_rolling_strategy(
            'format_rolling_strategy_options',
            14,
            self.open_ta.rolling_strategy_options,
            'position'
        )

    def test_format_rolling_strategy_market_time(self):
        """
        Test format_rolling_strategy_market_time
        """
        self.sub_format_rolling_strategy(
            'format_rolling_strategy_market_time',
            9,
            ['move_to_market_time_start', 'move_to_market_time_end'],
            'move_to_market_time'
        )

    def test_format_rolling_strategy_active_time(self):
        """
        Test format_rolling_strategy_active_time
        """
        self.sub_format_rolling_strategy(
            'format_rolling_strategy_active_time',
            9,
            ['active_time_start', 'active_time_end'],
            'active_time'
        )

    def test_set_rolling_strategy(self):
        """
        Test set rolling_strategy
        """
        result_keys = [
            'status', 'move_to_market_time_end', 'right', 'strike', 'days_begin',
            'new_expire_date', 'symbol', 'ex_month', 'call_by', 'contract', 'order_price',
            'ex_year', 'move_to_market_time_start', 'active_time_start', 'side',
            'active_time_end'
        ]

        self.set_sections(
            method='set_rolling_strategy',
            prop='rolling_strategy',
            length=16,
            keys=result_keys
        )

        # correct format
        for rolling_strategy in self.open_ta.rolling_strategy:
            self.assertEqual(type(rolling_strategy['side']), int)
            self.assertEqual(type(rolling_strategy['right']), int)
            self.assertEqual(type(rolling_strategy['side']), int)
            self.assertEqual(type(rolling_strategy['strike']), float)

            self.assertTrue(datetime.strptime(rolling_strategy['active_time_start'], '%H:%M:%S'))
            self.assertTrue(datetime.strptime(rolling_strategy['active_time_end'], '%H:%M:%S'))
            self.assertTrue(datetime.strptime(rolling_strategy['move_to_market_time_start'], '%H:%M:%S'))
            self.assertTrue(datetime.strptime(rolling_strategy['move_to_market_time_end'], '%H:%M:%S'))

    def test_ready(self):
        """
        Test ready file then return data
        """
        keys = ['working_order', 'filled_order',
                'cancelled_order', 'rolling_strategy']

        for fname in self.fnames:
            data = open(fname).read()

            print 'fname: %s' % fname

            open_ta = OpenTA(data=data)

            result = open_ta.read()
            self.assertEqual(type(result), dict)
            self.assertEqual(len(result), 4)

            pprint(result, width=400)

            for key in result.keys():
                self.assertEqual(type(result[key]), list)

                self.assertIn(key, keys)

            print '\n' + '-' * 100 + '\n'

    def test_read(self):
        """
        Test most important part in class
        """
        keys = ['working_order', 'filled_order', 'cancelled_order', 'rolling_strategy']

        for fname in self.fnames:
            data = open(fname).read()

            print 'fname: %s' % fname

            open_acc = OpenTA(data=data)

            result = open_acc.read()
            self.assertEqual(type(result), dict)
            self.assertEqual(len(result), 4)

            pprint(result, width=200)

            for key in result.keys():
                if key == 'summary':
                    self.assertEqual(type(result[key]), dict)
                else:
                    self.assertEqual(type(result[key]), list)

                self.assertIn(key, keys)

            print '\n' + '-' * 100 + '\n'


















