from lib.test import TestSetUp
from pms_app.tests import TestSetUpUnderlying
from pms_app.pos_app import models
from pprint import pprint


class TestPositionStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.date = '2014-08-01'

        self.items = {
            'available': 1873.49,
            'bp_adjustment': 0.0,
            'futures_bp': 1873.49,
            'pl_ytd': -5609.52,
            'cash_sweep': 3773.49
        }

        self.pos_statement = models.PositionStatement(date=self.date, **self.items)
        self.pos_statement.save()

    def test_save(self):
        """
        Test sample data save into db
        """
        print 'sample data:'
        pprint(self.items)

        print '\n' + 'Position Statement saved!\n'

        self.assertTrue(self.pos_statement.id)
        print 'Position Statement id: %d' % self.pos_statement.id

        print 'Position Statement data:'
        print self.pos_statement.__unicode__()[:80] + '...'

    def test_json(self):
        """
        Test json output
        """
        print 'pos in normal: %s' % self.pos_statement
        print 'pos in json: \n%s\n' % self.pos_statement.json()

        json = eval(self.pos_statement.json())

        print 'convert into dict:'
        pprint(json)
        keys = ("date", "cash_sweep", "pl_ytd", "futures_bp", "bp_adjustment", "available")

        for key in json.keys():
            self.assertIn(key, keys)


class TestSetUpPosUnd(TestSetUpUnderlying):
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

        self.position_statement = models.PositionStatement(date=self.date, **self.items)
        self.position_statement.save()


class TestPositionInstrumentUnd(TestSetUpPosUnd):
    def setUp(self):
        TestSetUpPosUnd.setUp(self)

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

        self.pos_ins = models.PositionInstrument()
        self.pos_ins.position_statement = self.position_statement
        self.pos_ins.underlying = self.underlying
        self.pos_ins.set_dict(self.items)

    def test_save(self):
        """
        Test set dict data into pos instrument
        """
        self.pos_ins.save()
        print 'PositionInstrument saved!\n'
        print 'pos id: %d' % self.pos_ins.id
        self.assertTrue(self.pos_ins.id)

    def test_json(self):
        """
        Test output json data format
        """
        print 'pos in normal: %s' % self.pos_ins
        print 'pos in json: \n%s\n' % self.pos_ins.json()

        json = eval(self.pos_ins.json())

        print 'convert into dict:'
        pprint(json)

        keys = ("name", "quantity", "days", "trade_price", "mark", "mark_change",
                "delta", "gamma", "theta", "vega", "pct_change", "pl_open",
                "pl_day", "bp_effect")

        for key in json.keys():
            self.assertIn(key, keys)


class TestSetUpPosUndIns(TestSetUpPosUnd):
    def setUp(self):
        TestSetUpPosUnd.setUp(self)

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

        self.instrument = models.PositionInstrument()
        self.instrument.position_statement = self.position_statement
        self.instrument.underlying = self.underlying
        self.instrument.set_dict(self.items)
        self.instrument.save()


class TestPositionStockUnd(TestSetUpPosUndIns):
    def setUp(self):
        TestSetUpPosUndIns.setUp(self)

        self.items = {
            'mark_change': 6.38, 'name': 'BAIDU INC ADR', 'pl_open': 38.6, 'days': 0.0, 'mark': 223.0,
            'vega': 0.0, 'pl_day': -63.8, 'delta': -10.0, 'bp_effect': 0.0, 'theta': 0.0,
            'pct_change': 0.0, 'quantity': -10.0, 'gamma': 0.0, 'trade_price': 226.86
        }

        self.pos_stock = models.PositionStock()
        self.pos_stock.position_statement = self.position_statement
        self.pos_stock.underlying = self.underlying
        self.pos_stock.instrument = self.instrument
        self.pos_stock.set_dict(self.items)

    def test_save(self):
        """
        Test save dict data into pos stock
        """
        self.pos_stock.save()
        print 'PositionStock saved!\n'
        print 'pos id: %d' % self.pos_stock.id
        self.assertTrue(self.pos_stock.id)

    def test_json(self):
        """
        Test output json data format
        """
        print 'pos in normal: %s' % self.pos_stock
        print 'pos in json: \n%s\n' % self.pos_stock.json()

        json = eval(self.pos_stock.json())

        print 'convert into dict:'
        pprint(json)

        keys = ("name", "quantity", "days", "trade_price", "mark", "mark_change",
                "delta", "gamma", "theta", "vega", "pct_change", "pl_open",
                "pl_day", "bp_effect")

        for key in json.keys():
            self.assertIn(key, keys)


class TestPositionOptionUnd(TestSetUpPosUndIns):
    def setUp(self):
        TestSetUpPosUndIns.setUp(self)

        self.items = [
            {'name': {'ex_month': 'AUG', 'right': '100', 'strike_price': '58.5',
                      'contract': 'PUT', 'ex_year': '14', 'special': 'Normal'},
             'mark_change': -0.63, 'pl_open': -219.0, 'days': 15.0,
             'mark': 0.38, 'vega': 18.07, 'pl_day': -189.0, 'delta': 52.79,
             'bp_effect': 0.0, 'theta': -9.71, 'pct_change': 0.0,
             'quantity': 3.0, 'gamma': 18.98, 'trade_price': 1.11},
            {'name': {'ex_month': 'AUG', 'right': '100', 'strike_price': '72.5',
                      'contract': 'CALL', 'ex_year': '14', 'special': 'Normal'},
             'mark_change': -0.14, 'pl_open': 57.0, 'days': 15.0,
             'mark': 0.06, 'vega': -6.02, 'pl_day': 42.0, 'delta': -11.92,
             'bp_effect': 0.0, 'theta': 3.11, 'pct_change': 0.0,
             'quantity': -3.0, 'gamma': -6.74, 'trade_price': 0.25}
        ]

    def test_save(self):
        """
        Test save dict data into pos options
        """

        for item in self.items:
            pos_option = models.PositionOption()
            pos_option.position_statement = self.position_statement
            pos_option.underlying = self.underlying
            pos_option.instrument = self.instrument
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

            print ''
