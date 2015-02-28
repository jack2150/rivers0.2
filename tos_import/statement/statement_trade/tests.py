from datetime import datetime
from glob import glob
import os
from pprint import pprint
# noinspection PyUnresolvedReferences
from django.utils.timezone import utc
from tos_import.files.real_files import real_path
from tos_import.files.test_files import *
from tos_import.classes.io.open_ta import OpenTA
from tos_import.classes.test import TestSetUp
from tos_import.statement.statement_trade import models
from tos_import.tests import TestReadyStatement


class TestTaModel(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.ta_model = models.TaModel()

        self.underlying = models.Underlying(
            symbol='TSLA',
            company='TESLA MOTORS INC COM',
        )
        self.underlying.save()

        self.future = models.Future(
            lookup='ES',
            symbol='/ESZ4',
            description='E-mini S&P 500 Index Futures',
            expire_date='DEC 14',
            session='ETH',
            spc='1/50'
        )
        self.future.save()

        self.future_without_symbol = models.Future(
            lookup='ES',
            symbol='',
            description='E-mini S&P 500 Index Futures',
            expire_date='DEC 14',
            session='ETH',
            spc='1/50'
        )
        self.future_without_symbol.save()

        self.forex = models.Forex(
            symbol='AUD/USD',
            description='AusDollar/US Dollar Spot',
        )
        self.forex.save()

    def test_get_symbol(self):
        """
        Test get symbol from either underlying or future or forex
        """
        foreign_key_sets = [
            ('Underlying', 'TSLA', dict(
                underlying=self.underlying,
                future=None,
                forex=None
            )),
            ('Future', '/ESZ4', dict(
                underlying=None,
                future=self.future,
                forex=None
            )),
            ('Future', '/ES', dict(
                underlying=None,
                future=self.future_without_symbol,
                forex=None
            )),
            ('Forex', 'AUD/USD', dict(
                underlying=None,
                future=None,
                forex=self.forex
            ))
        ]

        for cls_name, expect_result, key_set in foreign_key_sets:
            self.ta_model.underlying = key_set['underlying']
            self.ta_model.future = key_set['future']
            self.ta_model.forex = key_set['forex']
            symbol = self.ta_model.get_symbol()

            print 'get symbol from %s: %s' % (cls_name, symbol)
            self.assertEqual(symbol, expect_result)


class TestTradeActivity(TestReadyStatement):
    def setUp(self):
        TestReadyStatement.setUp(self)

        self.date = '2014-09-19'
        self.items = [self.date]
        self.trade_summary = models.TradeSummary(
            statement=self.statement,
            date=self.date
        )

        self.cls_var = self.trade_summary
        self.expect_keys = ['statement', 'date']

    def test_save(self):
        """
        Method use for test saving data into db
        """
        if self.cls_var:
            print 'sample date: '
            pprint(self.items)

            self.cls_var.save()

            print '\n' + '%s saved!' % self.cls_var.__class__.__name__
            print '%s id: %d' % (self.cls_var.__class__.__name__, self.cls_var.id)

            self.assertTrue(self.cls_var.id)

    def test_json_output(self):
        """
        Method use for test json output
        """
        if self.cls_var:
            cls_name = self.cls_var.__class__.__name__
            print '%s in normal: %s' % (cls_name, self.cls_var.__unicode__())
            print '%s in json: \n%s\n' % (cls_name, self.cls_var.json())

            json = eval(self.cls_var.json())

            print 'dict:'
            print json.keys()

            print 'convert into dict:'
            pprint(json)

            for key in json.keys():
                self.assertIn(key, self.expect_keys)


class TestWorkingOrder(TestTradeActivity):
    def setUp(self):
        TestTradeActivity.setUp(self)
        self.trade_summary.save()

        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)

        self.items = {
            'status': 'WORKING', 'pos_effect': 'AUTO', 'quantity': -100, 'symbol': 'FB',
            'contract': 'STOCK', 'order': 'LMT', 'time_placed': use_dt, 'spread': 'STOCK',
            'expire_date': '', 'strike': 0.0, 'tif': 'GTC', 'mark': 74.5, 'price': 82.0,
            'side': 'SELL'
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.working_order = models.WorkingOrder(
            trade_summary=self.trade_summary,
            underlying=self.underlying
        )
        self.working_order.set_dict(self.items)

        self.cls_var = self.working_order
        self.expect_keys = [
            'status', 'pos_effect', 'price', 'time_placed', 'date', 'mark', 'contract', 'side',
            'spread', 'expire_date', 'strike', 'tif', 'order', 'symbol', 'quantity'
        ]


class TestFilledOrder(TestTradeActivity):
    def setUp(self):
        TestTradeActivity.setUp(self)
        self.trade_summary.save()

        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)
        self.items = {
            'pos_effect': 'AUTO', 'exec_time': use_dt, 'net_price': 1.05, 'symbol': 'GOOG',
            'contract': 'PUT', 'side': 'BUY', 'price': 10.8, 'spread': 'VERTICAL',
            'expire_date': 'SEP 14', 'strike': 582.5, 'order': 'MKT', 'quantity': 1
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.filled_order = models.FilledOrder(
            trade_summary=self.trade_summary,
            underlying=self.underlying
        )
        self.filled_order.set_dict(self.items)

        self.cls_var = self.filled_order
        self.expect_keys = [
            'pos_effect', 'exec_time', 'price', 'date', 'net_price', 'contract', 'side', 'spread',
            'expire_date', 'strike', 'order', 'symbol', 'quantity'
        ]


class TestCancelledOrder(TestTradeActivity):
    def setUp(self):
        TestTradeActivity.setUp(self)
        self.trade_summary.save()

        use_dt = datetime(2014, 9, 28, 16, 16, 42, 462000, tzinfo=utc)
        self.items = {
            'status': 'CANCELED', 'pos_effect': 'AUTO', 'time_cancelled': use_dt,
            'price': 82.0, 'contract': 'STOCK', 'side': 'SELL', 'symbol': 'FB',
            'spread': 'STOCK', 'expire_date': '', 'strike': 0.0, 'tif': 'DAY',
            'order': 'LMT', 'quantity': -100
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.cancelled_order = models.CancelledOrder(
            trade_summary=self.trade_summary,
            underlying=self.underlying
        )
        self.cancelled_order.set_dict(self.items)

        self.cls_var = self.cancelled_order
        self.expect_keys = [
            'status', 'pos_effect', 'price', 'date', 'time_cancelled', 'contract', 'side', 'spread',
            'expire_date', 'strike', 'tif', 'order', 'symbol', 'quantity'
        ]


class TestRollingStrategy(TestTradeActivity):
    def setUp(self):
        TestTradeActivity.setUp(self)
        self.trade_summary.save()

        self.items = {
            'status': 'WAIT TRG', 'right': 100, 'strike': 77.5, 'days_begin': 2.0,
            'new_expire_date': 'NOV4 14', 'symbol': 'FB', 'ex_month': 'NOV',
            'call_by': 'Strike +1 ATM', 'contract': 'CALL', 'order_price': 'AUTO',
            'ex_year': 14, 'move_to_market_time_start': '11:00:00', 'active_time_start': '08:45:00',
            'active_time_end': '09:00:00', 'side': -1, 'move_to_market_time_end': '14:45:00'
        }

        self.underlying = models.Underlying(
            symbol=self.items['symbol'],
            company=''
        )
        self.underlying.save()

        self.rolling_strategy = models.RollingStrategy(
            trade_summary=self.trade_summary,
            underlying=self.underlying
        )
        self.rolling_strategy.set_dict(self.items)

        self.cls_var = self.rolling_strategy
        self.expect_keys = [
            'ex_month', 'days_begin', 'right', 'strike_price', 'move_to_market_time_end',
            'new_expire_date', 'symbol', 'contract', 'strategy', 'call_by', 'status', 'order_price',
            'ex_year', 'date', 'move_to_market_time_start', 'active_time_start', 'side',
            'active_time_end'
        ]


# noinspection PyUnresolvedReferences
class TestOpenTASaveAll(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.ta_files = glob(test_ta_path + '/*.csv')
        self.ta_files = self.ta_files + [
            os.path.join(test_path, '2014-11-25', '2014-11-25-TradeActivity.csv')
        ]

    def insert_db(self, no, trade_activity, test_model, data_list):
        """
        Save related data into model with pos statement
        :param no: int
        :param trade_activity: TradeActivity
        :param test_model: any models.class
        :param data_list: list of dict
        """
        ids = list()
        for data in data_list:
            # if symbol key exists in data_list
            if 'symbol' in data.keys():
                test_cls = test_model(trade_summary=trade_activity)

                underlying_obj = models.Underlying.objects.filter(symbol=data['symbol'])
                if underlying_obj.count():
                    underlying = underlying_obj.first()
                else:
                    company = ''
                    if 'description' in data.keys():
                        company = data['description']

                    underlying = models.Underlying(
                        symbol=data['symbol'],
                        company=company
                    )
                    underlying.save()

                test_cls.underlying = underlying
                test_cls.set_dict(data)
                test_cls.save()
            else:
                test_cls = test_model(trade_summary=trade_activity)
                test_cls.set_dict(data)
                test_cls.save()

            ids.append(test_cls.id)

        print '%d. save %s... ids: %s' % (
            no, test_model.__name__, ids
        )

        for saved_cls in test_model.objects.all():
            print saved_cls.id, saved_cls, saved_cls.json()

    def test_read_save(self):
        """
        Open TA file data then save all fields into db
        """
        for key, ta_file in enumerate(self.ta_files, start=1):
            print '%d. run filename: %s' % (key, ta_file)
            print 'starting...\n'

            date = os.path.basename(ta_file)[0:10]
            data = open(ta_file).read()

            statement = models.Statement(
                date=date,
                account_statement='None',
                position_statement='None',
                trade_activity=data,
            )
            statement.save()

            trade_activity = models.TradeSummary(
                statement=statement,
                date=date
            )
            trade_activity.save()

            print 'statement id: %d' % statement.id
            print 'trade_activity id: %d' % trade_activity.id

            print 'using open_ta to make dict data...'
            ta_data = OpenTA(data=data).read()

            print 'keys: %s\n' % ta_data.keys()

            self.insert_db(
                no=key,
                trade_activity=trade_activity,
                test_model=models.FilledOrder,
                data_list=ta_data['filled_order']
            )

            self.insert_db(
                no=key,
                trade_activity=trade_activity,
                test_model=models.CancelledOrder,
                data_list=ta_data['cancelled_order']
            )

            self.insert_db(
                no=key,
                trade_activity=trade_activity,
                test_model=models.WorkingOrder,
                data_list=ta_data['working_order']
            )

            self.insert_db(
                no=key,
                trade_activity=trade_activity,
                test_model=models.RollingStrategy,
                data_list=ta_data['rolling_strategy']
            )

            print '\n' + '-' * 100


# noinspection PyUnresolvedReferences
class TestSaveTradeActivity(TestSetUp):
    def setUp(self):
        TestSetUp.setUp(self)

        self.ta_files = glob(test_ta_path + '/*.csv')
        self.ta_files = [
            os.path.join(real_path, '2015-02-27', '2015-02-28-TradeActivity.csv')
        ]

    def ready_account_statement(self):
        """
        Test method for ready up account statement
        """
        ta_file = self.ta_files[0]
        date = os.path.basename(ta_file)[0:10]
        print 'Date: %s' % date

        ta_data = open(ta_file).read()

        statement = models.Statement(
            date=date,
            account_statement='None',
            position_statement=ta_data,
            trade_activity='None',
        )
        statement.save()

        self.save_ta = models.SaveTradeActivity(
            date=date,
            statement=statement,
            file_data=ta_data
        )

    def test_save_trade_activity(self):
        """
        Test save trade activity into db
        """
        self.ready_account_statement()
        self.save_ta.save_trade_activity()

        print 'TradeActivity count: %d' % models.TradeSummary.objects.count()
        self.assertGreaterEqual(models.TradeSummary.objects.count(), 1)

    def test_save_single(self):
        """
        Test save single order into db with
        underlying, future or forex foreign key
        """
        self.ready_account_statement()
        self.save_ta.save_trade_activity()

        self.save_ta.save_single(
            save_cls=models.WorkingOrder, save_data=self.save_ta.working_order
        )
        self.save_ta.save_single(
            save_cls=models.FilledOrder, save_data=self.save_ta.filled_order
        )
        self.save_ta.save_single(
            save_cls=models.CancelledOrder, save_data=self.save_ta.cancelled_order
        )

        print 'Underlying count: %d' % models.Underlying.objects.count()
        print 'Future count: %d' % models.Future.objects.count()
        print 'Forex count: %d' % models.Forex.objects.count()
        print 'WorkingOrder count: %d' % models.WorkingOrder.objects.count()
        print 'FilledOrder count: %d' % models.FilledOrder.objects.count()
        print 'CancelledOrder count: %d' % models.CancelledOrder.objects.count()

        self.assertGreaterEqual(models.Underlying.objects.count(), 1)
        self.assertGreaterEqual(models.Future.objects.count(), 1)
        self.assertGreaterEqual(models.Forex.objects.count(), 1)
        self.assertGreaterEqual(models.WorkingOrder.objects.count(), 1)
        self.assertGreaterEqual(models.FilledOrder.objects.count(), 1)
        self.assertGreaterEqual(models.CancelledOrder.objects.count(), 1)

    def test_save_rolling_strategy(self):
        """
        Test save rolling strategy into db
        :return:
        """
        self.ready_account_statement()
        self.save_ta.save_trade_activity()

        self.save_ta.save_rolling_strategy()

        print 'Underlying count: %d' % models.Underlying.objects.count()
        print 'RollingStrategy count: %d' % models.RollingStrategy.objects.count()

        self.assertGreaterEqual(models.Underlying.objects.count(), 0)
        self.assertGreaterEqual(models.RollingStrategy.objects.count(), 0)

    def test_save_all(self):
        """
        Test save all data from pos_data into models
        :return: None
        """
        for no, ta_file in enumerate(self.ta_files, start=1):
            print '%d. run filename: %s' % (no, ta_file)
            print 'starting...\n'

            date = os.path.basename(ta_file)[0:10]
            ta_data = open(ta_file).read()

            statement = models.Statement(
                date=date,
                account_statement='None',
                position_statement=ta_data,
                trade_activity='None',
            )
            statement.save()

            save_ta = models.SaveTradeActivity(
                date=date,
                statement=statement,
                file_data=ta_data
            )
            save_ta.save_all()

            print 'Statement count: %d' % models.Statement.objects.count()
            print 'TradeActivity count: %d' % models.TradeSummary.objects.count()

            print 'Underlying count: %d' % models.Underlying.objects.count()
            print 'Future count: %d' % models.Future.objects.count()
            print 'Forex count: %d' % models.Forex.objects.count()

            print 'WorkingOrder count: %d' % models.WorkingOrder.objects.count()
            print 'FilledOrder count: %d' % models.FilledOrder.objects.count()
            print 'CancelledOrder count: %d' % models.CancelledOrder.objects.count()
            print 'RollingStrategy count: %d\n' % models.RollingStrategy.objects.count()

            self.assertEqual(models.Statement.objects.count(), no)
            self.assertEqual(models.TradeSummary.objects.count(), no)

            self.assertGreaterEqual(models.Underlying.objects.count(), 0)
            self.assertGreaterEqual(models.Future.objects.count(), 0)
            self.assertGreaterEqual(models.Forex.objects.count(), 0)

            self.assertGreaterEqual(models.WorkingOrder.objects.count(), 0)
            self.assertGreaterEqual(models.FilledOrder.objects.count(), 0)
            self.assertGreaterEqual(models.CancelledOrder.objects.count(), 0)
            self.assertGreaterEqual(models.RollingStrategy.objects.count(), -1)
