import os
from pprint import pprint
from lib.test import TestSetUp
from lib.io.open_ta import OpenTA
from rivers.settings import FILES


class TestOpenTA(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.fnames = ['2014-09-19-TradeActivity.csv']

        self.test_file = os.path.join(FILES['trade_activity'], self.fnames[0])

        self.open_ta = OpenTA(fname=self.test_file)

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

    def test_set_rolling_strategy(self):
        """
        Test set rolling_strategy
        """
        self.set_sections(
            method='set_rolling_strategy',
            prop='rolling_strategy',
            length=13,
            keys=self.open_ta.rolling_strategy_keys
        )

    def test_ready(self):
        """
        Test ready file then return data
        """
        keys = ['working_order', 'filled_order',
                'cancelled_order', 'rolling_strategy']

        for fname in self.fnames:
            path = os.path.join(FILES['trade_activity'], fname)

            print 'fname: %s' % fname
            print 'path: %s' % path

            open_ta = OpenTA(path)

            result = open_ta.read()
            self.assertEqual(type(result), dict)
            self.assertEqual(len(result), 4)

            pprint(result, width=200)

            for key in result.keys():
                self.assertEqual(type(result[key]), list)

                self.assertIn(key, keys)

            print '\n' + '-' * 100 + '\n'




















