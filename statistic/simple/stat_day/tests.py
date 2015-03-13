import os
from pprint import pprint
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from tos_import.classes.tests import TestSetUpDB
from tos_import.statement.statement_account.models import SaveAccountStatement
from tos_import.statement.statement_position.models import SavePositionStatement
from tos_import.statement.statement_trade.models import *
from tos_import.files.test_files import test_path
from statistic.simple.stat_day import models
from statistic.simple.stat_day.models import SaveStatDay


class TestSaveData(TestSetUpDB):
    def setUp(self):
        TestSetUpDB.setUp(self)

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


class TestStatDay(TestSaveData):
    def setUp(self):
        TestSaveData.setUp(self)

        self.statement = Statement(
            date='2014-08-01',
            account_statement='',
            position_statement='',
            trade_activity=''
        )
        self.statement.save()

        self.items = dict(
            total_holding_count=20,
            total_order_count=10,
            working_order_count=3,
            filled_order_count=5,
            cancelled_order_count=2,
            account_pl_ytd=15654.55,
            account_pl_day=4412.11,
            holding_pl_day=4561.41,
            holding_pl_open=4561.33,
            commission_day=156.66,
            commission_ytd=172.66,
            option_bp_day=13242.33,
            stock_bp_day=4561.22
        )

        self.test_cls = models.StatDay(**self.items)
        self.test_cls.statement = self.statement
        self.expect_keys = [
            'total_holding_count',
            'total_order_count',
            'working_order_count',
            'filled_order_count',
            'cancelled_order_count',
            'account_pl_ytd',
            'account_pl_day',
            'holding_pl_day',
            'holding_pl_open',
            'commission_day',
            'commission_ytd',
            'option_bp_day',
            'stock_bp_day'
        ]


class TestStatDayHolding(TestSaveData):
    def setUp(self):
        TestSaveData.setUp(self)

        self.statement = Statement(
            date='2014-08-01',
            account_statement='',
            position_statement='',
            trade_activity=''
        )
        self.statement.save()

        self.items = dict(
            total_holding_count=20,
            total_order_count=10,
            working_order_count=3,
            filled_order_count=5,
            cancelled_order_count=2,
            account_pl_ytd=15654.55,
            account_pl_day=4412.11,
            holding_pl_day=4561.41,
            holding_pl_open=4561.33,
            commission_day=156.66,
            commission_ytd=172.66,
            option_bp_day=13242.33,
            stock_bp_day=4561.22
        )

        self.stat_day = models.StatDay(**self.items)
        self.stat_day.statement = self.statement
        self.stat_day.save()

        self.items = dict(
            name='Equity',
            total_order_count=5,
            working_order_count=3,
            filled_order_count=1,
            cancelled_order_count=2,
            total_holding_count=10,
            profit_holding_count=7,
            loss_holding_count=3,
            pl_open_sum=399.52,
            profit_open_sum=519.85,
            loss_open_sum=120.33,
            pl_day_sum=111.60,
            profit_day_sum=160.60,
            loss_day_sum=49.00,
            bp_effect_sum=6000.80
        )
        self.test_cls = models.StatDayHolding(**self.items)
        self.test_cls.stat_day = self.stat_day
        self.expect_keys = [
            'name',
            'total_order_count',
            'working_order_count',
            'filled_order_count',
            'cancelled_order_count',
            'total_holding_count',
            'profit_holding_count',
            'loss_holding_count',
            'pl_open_sum',
            'profit_open_sum',
            'loss_open_sum',
            'pl_day_sum',
            'profit_day_sum',
            'loss_day_sum',
            'bp_effect_sum'
        ]


class TestStatDayOptionGreek(TestSaveData):
    def setUp(self):
        TestSaveData.setUp(self)

        self.statement = Statement(
            date='2014-08-01',
            account_statement='',
            position_statement='',
            trade_activity=''
        )
        self.statement.save()

        self.items = dict(
            total_holding_count=20,
            total_order_count=10,
            working_order_count=3,
            filled_order_count=5,
            cancelled_order_count=2,
            account_pl_ytd=15654.55,
            account_pl_day=4412.11,
            holding_pl_day=4561.41,
            holding_pl_open=4561.33,
            commission_day=156.66,
            commission_ytd=172.66,
            option_bp_day=13242.33,
            stock_bp_day=4561.22
        )

        self.stat_day = models.StatDay(**self.items)
        self.stat_day.statement = self.statement
        self.stat_day.save()

        self.items = dict(
            name='Equity',
            total_order_count=5,
            working_order_count=3,
            filled_order_count=1,
            cancelled_order_count=2,
            total_holding_count=10,
            profit_holding_count=7,
            loss_holding_count=3,
            pl_open_sum=399.52,
            profit_open_sum=519.85,
            loss_open_sum=120.33,
            pl_day_sum=111.60,
            profit_day_sum=160.60,
            loss_day_sum=49.00,
            bp_effect_sum=6000.80
        )
        self.stat_day_holding = models.StatDayHolding(**self.items)
        self.stat_day_holding.stat_day = self.stat_day
        self.stat_day_holding.save()

        self.items = dict(
            delta_sum=425.00,
            gamma_sum=89.13,
            theta_sum=412.33,
            vega_sum=123.59
        )

        self.test_cls = models.StatDayOptionGreek(**self.items)
        self.test_cls.stat_day_holding = self.stat_day_holding
        self.expect_keys = [
            'delta_sum', 'gamma_sum', 'theta_sum', 'vega_sum'
        ]


# noinspection PyMethodOverriding
class TestSaveDateStat(TestSetUpDB):
    def setUp(self):
        """
        open three file and save it into table then get data
        """
        TestSetUpDB.setUp(self)

        self.ready_file2(real_date='2014-11-17', file_date='2014-11-18')
        self.ready_file2(real_date='2014-11-18', file_date='2014-11-19')
        self.ready_file2(real_date='2014-11-24', file_date='2014-11-25')
        self.assertGreaterEqual(Statement.objects.count(), 1)

        self.statement = Statement.objects.last()

        # create instance now
        self.save_day_stat = SaveStatDay(statement=self.statement)

        self.expected_keys = [
            'name',
            'total_order_count',
            'working_order_count',
            'filled_order_count',
            'cancelled_order_count',
            'total_holding_count',
            'profit_holding_count',
            'loss_holding_count',
            'pl_open_sum',
            'profit_open_sum',
            'loss_open_sum',
            'pl_day_sum',
            'profit_day_sum',
            'loss_day_sum',
            'bp_effect_sum'
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

    def ready_file2(self, real_date, file_date):
        acc_data = open(os.path.join(test_path, file_date, '%s-AccountStatement.csv' % file_date)).read()
        pos_data = open(os.path.join(test_path, file_date, '%s-PositionStatement.csv' % file_date)).read()
        ta_data = open(os.path.join(test_path, file_date, '%s-TradeActivity.csv' % file_date)).read()

        statement = Statement()
        statement.date = real_date
        statement.account_statement = acc_data
        statement.position_statement = pos_data
        statement.trade_activity = ta_data
        statement.save()

        SaveAccountStatement(
            date=file_date,
            statement=statement,
            file_data=acc_data
        ).save_all()

        SavePositionStatement(
            date=file_date,
            statement=statement,
            file_data=pos_data
        ).save_all()

        SaveTradeActivity(
            date=file_date,
            statement=statement,
            file_data=ta_data
        ).save_all()

    def test_get_future(self):
        """
        Test get holding future detail from table
        using set foreign key reference
        """
        future = self.save_day_stat.get_future()

        self.assertEqual(type(future), dict)
        self.assertEqual(future['name'], 'FUTURE')
        for key in self.expected_keys:
            self.assertIn(key, future.keys())
            print '%s: %s' % (key, future[key])
            self.assertNotEqual(future[key], 0)

    def test_get_forex(self):
        """
        Test get holding forex detail from table
        using set foreign key reference
        """
        forex = self.save_day_stat.get_forex()
        self.assertEqual(type(forex), dict)
        self.assertEqual(forex['name'], 'FOREX')
        for key in self.expected_keys:
            self.assertIn(key, forex.keys())
            print '%s: %s' % (key, forex[key])

    def test_get_equity(self):
        """
        Test get holding stock detail from table
        using set foreign key reference
        """
        equity = self.save_day_stat.get_equity()
        self.assertEqual(type(equity), dict)
        self.assertEqual(equity['name'], 'EQUITY')

        for key in self.expected_keys + ['option_greek']:
            self.assertIn(key, equity.keys())
            print '%s: %s' % (key, equity[key])

    def test_get_option(self):
        """
        Test get holding option detail from table
        using set foreign key reference
        """
        option = self.save_day_stat.get_option()
        self.assertEqual(type(option), dict)
        self.assertEqual(option['name'], 'OPTION')

        for key in self.expected_keys + ['option_greek']:
            self.assertIn(key, option.keys())
            print '%s: %s' % (key, option[key])

    def test_get_holding_spread(self):
        """
        Test get holding option detail from table
        using set foreign key reference
        """
        spread = self.save_day_stat.get_spread()
        self.assertEqual(type(spread), dict)
        self.assertEqual(spread['name'], 'SPREAD')

        for key in self.expected_keys + ['option_greek']:
            self.assertIn(key, spread.keys())
            print '%s: %s' % (key, spread[key])

    def test_get_holding_hedge(self):
        """
        Test get holding option detail from table
        using set foreign key reference
        """
        spread = self.save_day_stat.get_hedge()
        self.assertEqual(type(spread), dict)
        self.assertEqual(spread['name'], 'HEDGE')

        for key in self.expected_keys + ['option_greek']:
            self.assertIn(key, spread.keys())
            print '%s: %s' % (key, spread[key])

    def test_get_day_stat(self):
        """
        Test get date stat
        """
        expected_keys = [
            'total_holding_count',
            'total_order_count',
            'working_order_count',
            'filled_order_count',
            'cancelled_order_count',
            'account_pl_ytd',
            'account_pl_day',
            'holding_pl_day',
            'holding_pl_open',
            'commission_day',
            'commission_ytd',
            'option_bp_day',
            'stock_bp_day'
        ]

        day_stat = self.save_day_stat.get_day_stat()
        self.assertEqual(type(day_stat), dict)

        for key in expected_keys:
            self.assertIn(key, day_stat.keys())
            self.assertNotEqual(day_stat[key], 0.0)
            print '%s: %s' % (key, day_stat[key])

    def test_get_option_greek(self):
        """
        Test get option greek for equity, option and spread
        """
        position_instruments = [p for p in self.save_day_stat.position_instrument.all()]

        print 'run get option greek using position instrument...'
        option_greek = self.save_day_stat.get_option_greek(position_instruments)

        print 'option greek result:'
        pprint(option_greek)

        self.assertNotEqual(option_greek['delta_sum'], 0.0)
        self.assertNotEqual(option_greek['gamma_sum'], 0.0)
        self.assertNotEqual(option_greek['theta_sum'], 0.0)
        self.assertNotEqual(option_greek['vega_sum'], 0.0)

    def test_start(self):
        """
        Test save all data into day stat models
        """
        day_stat_keys = [
            'total_holding_count',
            'total_order_count',
            'working_order_count',
            'filled_order_count',
            'cancelled_order_count',
            'account_pl_ytd',
            'account_pl_day',
            'holding_pl_day',
            'holding_pl_open',
            'commission_day',
            'commission_ytd',
            'option_bp_day',
            'stock_bp_day'
        ]

        investment_keys = [
            'name',
            'total_order_count',
            'working_order_count',
            'filled_order_count',
            'cancelled_order_count',
            'total_holding_count',
            'profit_holding_count',
            'loss_holding_count',
            'pl_open_sum',
            'profit_open_sum',
            'loss_open_sum',
            'pl_day_sum',
            'profit_day_sum',
            'loss_day_sum',
            'bp_effect_sum'
        ]

        stat_day_id = self.save_day_stat.save_all()
        print 'Stat day id: %d' % stat_day_id
        self.assertTrue(stat_day_id)

        self.assertEqual(models.StatDay.objects.count(), 1)
        self.assertEqual(models.StatDayHolding.objects.count(), 6)
        self.assertEqual(models.StatDayOptionGreek.objects.count(), 4)

        stat_day = models.StatDay.objects.first()
        stat_day_holding = models.StatDayHolding.objects.all()
        stat_day_option_greek = models.StatDayOptionGreek.objects.all()

        print 'date stat:'
        for key in day_stat_keys:
            print '%s: %s' % (key, getattr(stat_day, key))

        print '\n' + '-' * 80 + '\n\n' + 'investment stat:'
        for investment in stat_day_holding:
            for key in investment_keys:
                print '%s: %s' % (key, getattr(investment, key))

            print ''

        print '\n' + '-' * 80 + '\n\n' + 'option greek:'
        for option_greek in stat_day_option_greek:
            print option_greek
            for key in ['delta_sum', 'gamma_sum', 'theta_sum', 'vega_sum']:
                print '%s: %s' % (key, getattr(option_greek, key))
            print '\n'