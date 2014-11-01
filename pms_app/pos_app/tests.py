from glob import glob
from lib.io import OpenPos
from lib.test import TestSetUp
from pms_app.tests import TestSetUpUnderlying
from pms_app.pos_app import models
from pprint import pprint
from rivers.settings import FILES


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


class TestPositionStock(TestPositionInstrument):
    def setUp(self):
        TestPositionInstrument.setUp(self)
        self.position_instrument.save()

        self.items = {
            'mark_change': 6.38, 'name': 'BAIDU INC ADR', 'pl_open': 38.6, 'days': 0.0, 'mark': 223.0,
            'vega': 0.0, 'pl_day': -63.8, 'delta': -10.0, 'bp_effect': 0.0, 'theta': 0.0,
            'pct_change': 0.0, 'quantity': -10.0, 'gamma': 0.0, 'trade_price': 226.86
        }

        self.pos_stock = models.PositionStock()
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


class TestOpenPosSaveAll(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.pos_files = glob(FILES['position_statement'] + '/*.csv')

    def insert_db(self, no, position_statement, underlying, instrument, test_model, data):
        """
        Save related data into model with pos statement
        :param no: int
        :param position_statement: PositionStatement
        :param underlying: Underlying
        :param instrument: Instrument
        :param test_model: any models.class
        :param data: dict
        """
        test_cls = test_model(
            position_statement=position_statement,
            underlying=underlying
        )
        if instrument:
            test_cls.instrument = instrument

        test_cls.set_dict(data)
        test_cls.save()

        print '%d. save %s... id: %s' % (
            no, test_model.__name__, test_cls.id
        )

        return test_cls

    def test_read_save(self):
        """
        Open Pos file data then save all fields into db
        """
        for no, pos_file in enumerate(self.pos_files, start=1):
            print '%d. run filename: %s' % (no, pos_file)
            print 'starting...\n'

            date = pos_file[-32:-22]
            pos_data = open(pos_file).read()

            positions, overall = OpenPos(data=pos_data).read()

            statement = models.Statement(
                date=date,
                account_statement='None',
                position_statement=pos_data,
                trade_activity='None',
            )
            statement.save()

            position_statement = models.PositionStatement(
                statement=statement,
                date=date,
                **overall
            )
            position_statement.save()

            print 'statement id: %d' % statement.id
            print 'position_statement id: %d' % position_statement.id

            for key, position in enumerate(positions, start=1):
                print 'current symbol: %s' % position['symbol']

                # save underlying if not exists
                underlying_obj = models.Underlying.objects.filter(symbol=position['symbol'])
                if underlying_obj.count():
                    underlying = underlying_obj.first()
                    print 'using old underlying, id: %d' % underlying.id
                else:
                    underlying = models.Underlying(
                        symbol=position['symbol'],
                        company=position['company']
                    )
                    underlying.save()
                    print 'new underlying saved, id: %d' % underlying.id

                # save instrument
                instrument = self.insert_db(
                    no=key,
                    position_statement=position_statement,
                    underlying=underlying,
                    instrument=None,
                    test_model=models.PositionInstrument,
                    data=position['instrument']
                )

                # save stock
                self.insert_db(
                    no=key,
                    position_statement=position_statement,
                    underlying=underlying,
                    instrument=instrument,
                    test_model=models.PositionStock,
                    data=position['stock']
                )

                for option in position['options']:
                    self.insert_db(
                        no=key,
                        position_statement=position_statement,
                        underlying=underlying,
                        instrument=instrument,
                        test_model=models.PositionOption,
                        data=option
                    )

                print '\n' + '-' * 80

            print '\n' + '=' * 100


class TestSavePositionStatement(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.pos_files = glob(FILES['position_statement'] + '/*.csv')

    def test_save_all(self):
        """
        Test save all data from pos_data into models
        :return: None
        """
        for no, pos_file in enumerate(self.pos_files, start=1):
            print '%d. run filename: %s' % (no, pos_file)
            print 'starting...\n'

            date = pos_file[-32:-22]
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

            print 'statement count: %d' % models.Statement.objects.count()
            print 'position statement count: %d' % models.PositionStatement.objects.count()
            print 'position instrument count: %d' % models.PositionInstrument.objects.count()
            print 'position stock count: %d' % models.PositionStock.objects.count()
            print 'position options count: %d\n' % models.PositionOption.objects.count()

            self.assertEqual(models.Statement.objects.count(), no)
            self.assertEqual(models.PositionStatement.objects.count(), no)
            self.assertEqual(models.PositionInstrument.objects.count(),
                             models.PositionStock.objects.count())
            self.assertGreater(models.PositionOption.objects.count(), 0)
