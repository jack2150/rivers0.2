from glob import glob
import os
from app_pms.test_files import *
from app_pms.classes.io import OpenPos
from app_pms.classes.test import TestSetUp
from app_pms.tests import TestSetUpUnderlying
from app_pms.app_pos import models
from pprint import pprint


class TestPositionStatement(TestSetUpUnderlying):
    def setUp(self):
        TestSetUpUnderlying.setUp(self)

        self.date = '2014-08-01'
        self.items = {
            'available': 1873.49,
            'bp_adjustment': 0.0,
            'futures_bp': 1873.49,
            'pl_ytd': -5609.52,
            'cash_sweep': 3773.49
        }

        self.statement = models.Statement(
            date=self.date,
            account_statement='None',
            position_statement='None',
            trade_activity='Position raw data here...',
        )

        self.statement.save()

        self.position_statement = models.PositionStatement(
            statement=self.statement,
            date=self.date,
            **self.items
        )
        self.position_statement.save()

        self.test_cls = self.position_statement
        self.expect_keys = (
            "date", "cash_sweep", "pl_ytd", "futures_bp", "bp_adjustment", "available"
        )

    def test_save(self):
        """
        Method use for test saving data into db
        """
        if self.test_cls:
            print 'sample date: '
            pprint(self.items)

            self.test_cls.save()

            print '\n' + '%s saved!' % self.test_cls.__class__.__name__
            print '%s id: %d' % (self.test_cls.__class__.__name__, self.test_cls.id)

            self.assertTrue(self.test_cls.id)

    def test_json_output(self):
        """
        Method use for test json output
        """
        if self.test_cls:
            cls_name = self.test_cls.__class__.__name__
            print '%s in normal: %s' % (cls_name, self.test_cls.__unicode__())
            print '%s in json: \n%s\n' % (cls_name, self.test_cls.json())

            json = eval(self.test_cls.json())

            print 'dict:'
            print json.keys()

            print 'convert into dict:'
            pprint(json)

            for key in json.keys():
                self.assertIn(key, self.expect_keys)


class TestPositionInstrument(TestPositionStatement):
    def setUp(self):
        TestPositionStatement.setUp(self)
        self.position_statement.save()

        self.items = {
            'name': 'SPX',
            'mark_change': 0.0,
            'pl_open': -50.0,
            'days': 0.0,
            'mark': 0.0,
            'vega': 17.48,
            'pl_day': 92.5,
            'delta': 3.93,
            'bp_effect': 0.0,
            'theta': -11.96,
            'pct_change': -2.0,
            'quantity': 0.0,
            'gamma': 0.15,
            'trade_price': 0.0
        }

        self.position_instrument = models.PositionInstrument()
        self.position_instrument.position_statement = self.position_statement
        self.position_instrument.underlying = self.underlying
        self.position_instrument.set_dict(self.items)

        self.test_cls = self.position_instrument
        self.expect_keys = (
            "name", "quantity", "days", "trade_price", "mark", "mark_change",
            "delta", "gamma", "theta", "vega", "pct_change", "pl_open",
            "pl_day", "bp_effect"
        )


class TestPositionEquity(TestPositionInstrument):
    def setUp(self):
        TestPositionInstrument.setUp(self)
        self.position_instrument.save()

        self.items = {
            'mark_change': 6.38, 'name': 'BAIDU INC ADR', 'pl_open': 38.6, 'days': 0.0, 'mark': 223.0,
            'vega': 0.0, 'pl_day': -63.8, 'delta': -10.0, 'bp_effect': 0.0, 'theta': 0.0,
            'pct_change': 0.0, 'quantity': -10.0, 'gamma': 0.0, 'trade_price': 226.86
        }

        self.pos_stock = models.PositionEquity()
        self.pos_stock.position_statement = self.position_statement
        self.pos_stock.underlying = self.underlying
        self.pos_stock.instrument = self.position_instrument
        self.pos_stock.set_dict(self.items)

        self.test_cls = self.position_instrument
        self.expect_keys = (
            "name", "quantity", "days", "trade_price", "mark", "mark_change",
            "delta", "gamma", "theta", "vega", "pct_change", "pl_open",
            "pl_day", "bp_effect"
        )


class TestPositionOption(TestPositionInstrument):
    def setUp(self):
        TestPositionInstrument.setUp(self)
        self.position_instrument.save()

        self.items = [
            {'name': {'ex_month': 'AUG', 'right': '100', 'strike': '58.5',
                      'contract': 'PUT', 'ex_year': '14', 'special': 'Normal'},
             'mark_change': -0.63, 'pl_open': -219.0, 'days': 15.0,
             'mark': 0.38, 'vega': 18.07, 'pl_day': -189.0, 'delta': 52.79,
             'bp_effect': 0.0, 'theta': -9.71, 'pct_change': 0.0,
             'quantity': 3.0, 'gamma': 18.98, 'trade_price': 1.11},
            {'name': {'ex_month': 'AUG', 'right': '100', 'strike': '72.5',
                      'contract': 'CALL', 'ex_year': '14', 'special': 'Normal'},
             'mark_change': -0.14, 'pl_open': 57.0, 'days': 15.0,
             'mark': 0.06, 'vega': -6.02, 'pl_day': 42.0, 'delta': -11.92,
             'bp_effect': 0.0, 'theta': 3.11, 'pct_change': 0.0,
             'quantity': -3.0, 'gamma': -6.74, 'trade_price': 0.25}
        ]

        self.test_cls = None
        self.expect_keys = None

    def test_save(self):
        """
        Test save dict data into pos options
        """

        for item in self.items:
            pos_option = models.PositionOption()
            pos_option.position_statement = self.position_statement
            pos_option.underlying = self.underlying
            pos_option.instrument = self.position_instrument
            pos_option.set_dict(item)
            pos_option.save()

            print 'PositionOption saved!'
            print 'pos id: %d\n' % pos_option.id

            self.assertTrue(pos_option.id)

    def test_json(self):
        """
        Test output json data format
        """
        for item in self.items:
            pos_option = models.PositionOption()
            pos_option.position_statement = self.position_statement
            pos_option.underlying = self.underlying
            pos_option.set_dict(item)

            print 'pos in normal: %s' % pos_option
            print 'pos in json: \n%s\n' % pos_option.json()

            json = eval(pos_option.json())

            print 'convert into dict:'
            pprint(json)

            keys = ("name", "quantity", "days", "trade_price", "mark", "mark_change",
                    "delta", "gamma", "theta", "vega", "pct_change", "pl_open",
                    "pl_day", "bp_effect")

            for key in json.keys():
                self.assertIn(key, keys)


class TestPositionFuture(TestPositionStatement):
    def setUp(self):
        TestPositionStatement.setUp(self)

        self.items = {
            'mark_change': 1.25, 'pl_open': -212.5, 'symbol': '/ES', 'days': 35,
            'mark': 2039.25, 'pl_day': -62.5, 'bp_effect': -5060.0, 'pct_change': 0.26,
            'trade_price': 2035.0, 'quantity': -1
        }

        self.future = models.Future(
            symbol=self.items['symbol']
        )
        self.future.save()

        self.pos_future = models.PositionFuture(
            position_statement=self.position_statement,
            future=self.future
        )
        self.pos_future.set_dict(self.items)

        self.test_cls = self.pos_future
        self.expect_keys = (
            "symbol", "quantity", "days", "trade_price", "mark", "mark_change",
            "pct_change", "pl_open", "pl_day", "bp_effect"
        )


class TestPositionForex(TestPositionStatement):
    def setUp(self):
        TestPositionStatement.setUp(self)

        self.items = {
            'mark_change': 0.4975, 'pl_open': -13.16, 'symbol': 'USD/JPY',
            'mark': 116.335, 'pl_day': -13.16, 'bp_effect': -213.16, 'pct_change': 0.0,
            'trade_price': 116.473, 'quantity': 10000
        }

        self.forex = models.Forex(
            symbol=self.items['symbol']
        )
        self.forex.save()

        self.pos_forex = models.PositionForex(
            position_statement=self.position_statement,
            forex=self.forex
        )
        self.pos_forex.set_dict(self.items)

        self.test_cls = self.pos_forex
        self.expect_keys = (
            "symbol", "quantity", "trade_price", "mark", "mark_change",
            "pct_change", "pl_open", "pl_day", "bp_effect"
        )


class TestSavePositionStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.pos_files = glob(test_pos_path + '/*.csv')

        pos_file = self.pos_files[0]
        self.date = os.path.basename(pos_file)[0:10]
        self.pos_data = open(pos_file).read()

        self.statement = models.Statement(
            date=self.date,
            account_statement='None',
            position_statement=self.pos_data,
            trade_activity='None',
        )
        self.statement.save()

        self.save_pos = models.SavePositionStatement(
            date=self.date,
            statement=self.statement,
            file_data=self.pos_data,
        )

    def test_save_position_statement(self):
        """
        Test save position statement into db
        """
        self.save_pos.save_position_statement()

        print 'statement count: %d' % models.Statement.objects.count()
        print 'PositionStatement count: %d' % models.PositionStatement.objects.count()
        position_statement = models.PositionStatement.objects.first()
        pprint(position_statement)
        pprint(eval(position_statement.json()))
        self.assertEqual(models.Statement.objects.count(), 1)

    def test_save_future_position(self):
        """
        Test save future position list into db
        """
        self.save_pos.save_position_statement()
        self.save_pos.save_future_position()

        print 'Future count: %d' % models.Future.objects.count()
        print 'PositionFuture count: %d' % models.PositionFuture.objects.count()

        self.assertGreaterEqual(models.Future.objects.count(), 1)
        self.assertGreaterEqual(models.PositionFuture.objects.count(), 1)

        pos_futures = models.PositionFuture.objects.all()
        pprint(pos_futures)

        for future in models.Future.objects.all():
            print future
            #pprint(eval(future.json()), width=300)

        for pos_future in pos_futures:
            pprint(eval(pos_future.json()), width=300)

    def test_save_forex_position(self):
        """
        Test save future position list into db
        """
        self.save_pos.save_position_statement()
        self.save_pos.save_forex_position()

        print 'Forex count: %d' % models.Forex.objects.count()
        print 'PositionForex count: %d' % models.PositionForex.objects.count()

        self.assertGreaterEqual(models.Forex.objects.count(), 1)
        self.assertGreaterEqual(models.PositionForex.objects.count(), 1)

        pos_forexs = models.PositionForex.objects.all()
        pprint(pos_forexs)

        for pos_forex in pos_forexs:
            pprint(eval(pos_forex.json()), width=300)

    def test_save_equity_option_position(self):
        """
        Test save future position list into db
        """
        self.save_pos.save_position_statement()
        self.save_pos.save_equity_option_position()

        print 'Underlying count: %d' % models.Underlying.objects.count()
        print 'statement count: %d' % models.Statement.objects.count()
        print 'position statement count: %d' % models.PositionStatement.objects.count()
        print 'position instrument count: %d' % models.PositionInstrument.objects.count()
        print 'position stock count: %d' % models.PositionEquity.objects.count()
        print 'position options count: %d\n' % models.PositionOption.objects.count()

        self.assertEqual(models.Statement.objects.count(), 1)
        self.assertEqual(models.PositionStatement.objects.count(), 1)
        self.assertEqual(models.PositionInstrument.objects.count(),
                         models.PositionEquity.objects.count())
        self.assertGreater(models.PositionOption.objects.count(), 1)

    def test_save_all(self):
        """
        Test save all data from pos_data into models
        :return: None
        """
        for no, pos_file in enumerate(self.pos_files, start=1):
            print '%d. run filename: %s' % (no, pos_file)
            print 'starting...\n'

            date = os.path.basename(pos_file)[0:10]
            pos_data = open(pos_file).read()

            statement = models.Statement(
                date=date,
                account_statement='None',
                position_statement=pos_data,
                trade_activity='None',
            )
            statement.save()

            save_pos = models.SavePositionStatement(
                date=date,
                statement=statement,
                file_data=pos_data
            )
            save_pos.save_all()

            print 'Underlying count: %d' % models.Underlying.objects.count()
            print 'statement count: %d' % models.Statement.objects.count()
            print 'position statement count: %d' % models.PositionStatement.objects.count()
            print 'position instrument count: %d' % models.PositionInstrument.objects.count()
            print 'position stock count: %d' % models.PositionEquity.objects.count()
            print 'position options count: %d\n' % models.PositionOption.objects.count()
            print 'Forex count: %d' % models.Forex.objects.count()
            print 'PositionForex count: %d' % models.PositionForex.objects.count()
            print 'Future count: %d' % models.Future.objects.count()
            print 'PositionFuture count: %d' % models.PositionFuture.objects.count()

            self.assertGreaterEqual(models.Statement.objects.count(), 1)
            self.assertGreaterEqual(models.PositionStatement.objects.count(), 1)
            self.assertGreaterEqual(models.PositionInstrument.objects.count(),
                                    models.PositionEquity.objects.count())
            self.assertGreaterEqual(models.PositionOption.objects.count(), 1)
            self.assertGreaterEqual(models.Forex.objects.count(), 1)
            self.assertGreaterEqual(models.PositionForex.objects.count(), 1)
            self.assertGreaterEqual(models.Future.objects.count(), 1)
            self.assertGreaterEqual(models.PositionFuture.objects.count(), 1)
