import os
from pprint import pprint
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from tos_import.classes.test import TestSetUp
from tos_import.statement_trade.models import *
from tos_import.test_files import test_path
from stat_simple import models
from stat_simple.models import SaveDayStat


class TestSaveData(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.items = {}
        self.test_cls = None
        self.expect_keys = None

    def test_save(self):
        if self.test_cls:
            print 'sample date: '
            pprint(self.items)

            self.test_cls.save()
            self.assertTrue(self.test_cls.id)

            print '\n' + '%s saved!' % self.test_cls.__class__.__name__
            print '%s id: %d' % (self.test_cls.__class__.__name__, self.test_cls.id)

            print self.test_cls, '\n'

            for key in self.expect_keys:
                result = self.test_cls.__getattribute__(key)
                print '%s: %s' % (key, result)
                self.assertEqual(self.items[key], result)
        else:
            print 'skip test...'


class TestDateStat(TestSaveData):
    def setUp(self):
        TestSaveData.setUp(self)

        self.statement = Statement(
            date='2014-08-01',
            account_statement='',
            position_statement='',
            trade_activity=''
        )
        self.statement.save()

        self.items = {'c_day': 93.48,
                      'c_ytd': 266.82,
                      'cancelled_order': 4,
                      'filled_order': 17,
                      'option_bp_day': 4678.93,
                      'pl_day': 5029.98,
                      'pl_ytd': 19552.48,
                      'stock_bp_day': 4357.86,
                      'total_order': 27,
                      'working_order': 6}

        self.test_cls = models.DayStat(**self.items)
        self.test_cls.statement = self.statement
        self.expect_keys = ['total_order',
                            'c_day',
                            'cancelled_order',
                            'stock_bp_day',
                            'c_ytd',
                            'filled_order',
                            'pl_day',
                            'pl_ytd',
                            'working_order',
                            'option_bp_day']


class TestDayStatHolding(TestSaveData):
    def setUp(self):
        TestSaveData.setUp(self)

        self.statement = Statement(
            date='2014-08-01',
            account_statement='',
            position_statement='',
            trade_activity=''
        )
        self.statement.save()

        self.items = {'c_day': 93.48,
                      'c_ytd': 266.82,
                      'cancelled_order': 4,
                      'filled_order': 17,
                      'option_bp_day': 4678.93,
                      'pl_day': 5029.98,
                      'pl_ytd': 19552.48,
                      'stock_bp_day': 4357.86,
                      'total_order': 27,
                      'working_order': 6}

        self.day_stat = models.DayStat(**self.items)
        self.day_stat.statement = self.statement
        self.day_stat.save()

        self.items = dict(
            name='Equity',
            total_order=5,
            working_order=3,
            filled_order=1,
            cancelled_order=2,
            holding=10,
            profit_holding=7,
            loss_holding=3,
            pl_total=399.52,
            profit_total=519.85,
            loss_total=120.33,
        )
        self.test_cls = models.DayStatHolding(**self.items)
        self.test_cls.day_stat = self.day_stat
        self.expect_keys = [
            'name',
            'total_order', 'working_order', 'filled_order', 'cancelled_order',
            'holding', 'profit_holding', 'profit_holding',
            'pl_total', 'profit_total', 'loss_total'
        ]


# noinspection PyMethodOverriding
class TestSaveDateStat(TestSetUp):
    def setUp(self):
        """
        open three file and save it into table then get data
        """
        TestSetUp.setUp(self)

        self.ready_file(real_date='2014-11-17', file_date='2014-11-18')
        self.ready_file(real_date='2014-11-18', file_date='2014-11-19')
        self.ready_file(real_date='2014-11-24', file_date='2014-11-25')
        self.assertGreaterEqual(Statement.objects.count(), 1)

        self.statement = Statement.objects.last()

        # create instance now
        self.day_stat = SaveDayStat(statement=self.statement)

        self.expected_keys = [
            'name',
            'total_order', 'working_order', 'filled_order', 'cancelled_order',
            'holding', 'profit_holding', 'loss_holding',
            'pl_total', 'profit_total', 'loss_total',
        ]

    def ready_file(self, real_date, file_date):
        if not User.objects.exists():
            self.user = User.objects.create_superuser(
                username='jack',
                email='a@b.com',
                password='pass'
            )

        self.date = real_date

        self.account_statement_file = SimpleUploadedFile(
            '%s-AccountStatement.csv' % file_date,
            open(os.path.join(test_path, file_date, '%s-AccountStatement.csv' % file_date)).read()
        )
        self.position_statement_file = SimpleUploadedFile(
            '%s-PositionStatement.csv' % file_date,
            open(os.path.join(test_path, file_date, '%s-PositionStatement.csv' % file_date)).read()
        )
        self.trade_activity_file = SimpleUploadedFile(
            '%s-TradeActivity.csv' % file_date,
            open(os.path.join(test_path, file_date, '%s-TradeActivity.csv' % file_date)).read()
        )

        self.client.login(username='jack', password='pass')

        self.client.post(
            path=reverse('admin:statement_import'),
            data=dict(
                date=self.date,
                account_statement=self.account_statement_file,
                position_statement=self.position_statement_file,
                trade_activity=self.trade_activity_file
            )
        )

    def test_get_future(self):
        """
        Test get holding future detail from table
        using set foreign key reference
        """
        future = self.day_stat.get_future()
        self.assertEqual(type(future), dict)
        self.assertEqual(future['name'], 'future')
        for key in self.expected_keys:
            self.assertIn(key, future.keys())
            print '%s: %s' % (key, future[key])
            self.assertNotEqual(future[key], 0)

    def test_get_forex(self):
        """
        Test get holding forex detail from table
        using set foreign key reference
        """
        forex = self.day_stat.get_forex()
        self.assertEqual(type(forex), dict)
        self.assertEqual(forex['name'], 'forex')
        for key in self.expected_keys:
            self.assertIn(key, forex.keys())
            print '%s: %s' % (key, forex[key])

    def test_get_equity(self):
        """
        Test get holding stock detail from table
        using set foreign key reference
        """
        equity = self.day_stat.get_equity()
        self.assertEqual(type(equity), dict)
        self.assertEqual(equity['name'], 'equity')

        for key in self.expected_keys:
            self.assertIn(key, equity.keys())
            print '%s: %s' % (key, equity[key])

    def test_get_option(self):
        """
        Test get holding option detail from table
        using set foreign key reference
        """
        option = self.day_stat.get_option()
        self.assertEqual(type(option), dict)
        self.assertEqual(option['name'], 'option')

        for key in self.expected_keys:
            self.assertIn(key, option.keys())
            print '%s: %s' % (key, option[key])

    def test_get_holding_spread(self):
        """
        Test get holding option detail from table
        using set foreign key reference
        """
        spread = self.day_stat.get_spread()
        self.assertEqual(type(spread), dict)
        self.assertEqual(spread['name'], 'spread')

        for key in self.expected_keys:
            self.assertIn(key, spread.keys())
            print '%s: %s' % (key, spread[key])

    def test_get_day_stat(self):
        """
        Test get date stat
        """
        expected_keys = [
            'total_holding', 'total_order', 'cancelled_order', 'filled_order', 'working_order',
            'pl_ytd', 'pl_day', 'c_day', 'c_ytd', 'stock_bp_day', 'option_bp_day'
        ]

        day_stat = self.day_stat.get_day_stat()
        self.assertEqual(type(day_stat), dict)

        for key in expected_keys:
            self.assertIn(key, day_stat.keys())
            self.assertNotEqual(day_stat[key], 0.0)
            print '%s: %s' % (key, day_stat[key])

    def test_start(self):
        """

        :return:
        """
        day_stat_keys = [
            'total_holding', 'total_order', 'c_day', 'cancelled_order', 'stock_bp_day',
            'c_ytd', 'filled_order', 'pl_day', 'pl_ytd', 'working_order',
            'option_bp_day'
        ]

        investment_keys = [
            'name',
            'total_order', 'working_order', 'filled_order', 'cancelled_order',
            'holding', 'profit_holding', 'loss_holding',
            'pl_total', 'profit_total', 'loss_total',
        ]

        self.assertEqual(models.DayStat.objects.count(), 1 * 3)
        self.assertEqual(models.DayStatHolding.objects.count(), 5 * 3)

        day_stat = models.DayStat.objects.first()
        investments = models.DayStatHolding.objects.all()

        print 'date stat:'
        for key in day_stat_keys:
            print '%s: %s' % (key, getattr(day_stat, key))

        print '\n' + '-' * 80 + '\n\n' + 'investment stat:'
        for investment in investments:
            for key in investment_keys:
                print '%s: %s' % (key, getattr(investment, key))

            print ''
